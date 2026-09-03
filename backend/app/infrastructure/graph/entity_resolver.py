"""
Entity Resolver for NEXUS-RAG Knowledge Graph Intelligence (Phase 5).
Performs canonical name normalization, alias clustering, and fuzzy entity deduplication.
"""
from typing import Dict, List, Optional, Tuple, Set
import re
import uuid
from app.domain.models import EntityNode, EntityType, GraphProvenance
from app.core.logging import logger


class EntityResolver:
    """Resolves and merges duplicate entity mentions into unified canonical nodes."""

    # Suffixes and tokens to strip when computing canonical representation
    LEGAL_SUFFIXES = [
        r",?\s*\binc\.?\b",
        r",?\s*\bllc\b",
        r",?\s*\bcorp\.?\b",
        r",?\s*\bcorporation\b",
        r",?\s*\bltd\.?\b",
        r",?\s*\blimited\b",
        r",?\s*\bgmbh\b",
        r",?\s*\bag\b",
        r",?\s*\bco\.?\b",
        r",?\s*\bcompany\b"
    ]

    # Pre-defined known aliases mapping to canonical standard names
    CANONICAL_ALIASES: Dict[str, str] = {
        "openai inc": "OpenAI",
        "openai inc.": "OpenAI",
        "openai, inc.": "OpenAI",
        "openai llc": "OpenAI",
        "deepmind technologies": "DeepMind",
        "google deepmind": "Google DeepMind",
        "meta ai research": "Meta AI",
        "facebook ai research": "Meta AI",
        "fair": "Meta AI",
        "gpt4": "GPT-4",
        "gpt-4o": "GPT-4o",
        "gpt4o": "GPT-4o",
        "chatgpt": "ChatGPT",
        "bert base": "BERT",
        "bert large": "BERT",
        "attention is all you need paper": "Attention Is All You Need",
        "transformer architecture": "Transformer",
        "ms-marco": "MS MARCO",
        "msmarco": "MS MARCO",
    }

    def __init__(self):
        # Maps normalized key -> canonical EntityNode
        self.entities_by_key: Dict[str, EntityNode] = {}
        # Maps raw alias lowercase -> normalized key
        self.alias_to_key: Dict[str, str] = {}

    def normalize_name(self, raw_name: str) -> str:
        """
        Computes a clean, deduplicated canonical name string.
        E.g. 'OpenAI, Inc.' -> 'OpenAI'
        """
        clean = raw_name.strip(" \"'“”,.;:()")
        if not clean:
            return raw_name

        # Strip legal company suffixes
        for suffix in self.LEGAL_SUFFIXES:
            clean = re.sub(suffix, "", clean, flags=re.IGNORECASE).strip()

        # Normalize internal whitespace
        clean = re.sub(r"\s+", " ", clean).strip()

        # Check predefined alias mapping
        clean_lower = clean.lower()
        if clean_lower in self.CANONICAL_ALIASES:
            return self.CANONICAL_ALIASES[clean_lower]

        return clean

    def _get_lookup_key(self, name: str) -> str:
        """Computes a normalized lookup key for fuzzy indexing."""
        norm = self.normalize_name(name).lower()
        # Remove all non-alphanumeric chars for key comparison
        key = re.sub(r"[^a-z0-9]", "", norm)
        return key if key else norm

    def resolve_entity(
        self,
        raw_name: str,
        entity_type: EntityType,
        provenance: Optional[GraphProvenance] = None
    ) -> EntityNode:
        """
        Resolves an extracted mention to an existing canonical EntityNode or creates a new one.
        Maintains alias lists, mention counts, and provenance history.
        """
        canonical_name = self.normalize_name(raw_name)
        lookup_key = self._get_lookup_key(canonical_name)
        raw_lower = raw_name.lower().strip()

        # 1. Check if raw mention is directly mapped in aliases
        if raw_lower in self.alias_to_key:
            target_key = self.alias_to_key[raw_lower]
            if target_key in self.entities_by_key:
                node = self.entities_by_key[target_key]
                self._update_node(node, raw_name, provenance)
                return node

        # 2. Check if normalized key already exists
        if lookup_key in self.entities_by_key:
            node = self.entities_by_key[lookup_key]
            self._update_node(node, raw_name, provenance)
            return node

        # 3. Check for prefix/suffix containment or high token overlap in existing keys
        for existing_key, existing_node in self.entities_by_key.items():
            if self._is_fuzzy_match(lookup_key, existing_key, raw_name, existing_node.canonical_name):
                self._update_node(existing_node, raw_name, provenance)
                self.alias_to_key[raw_lower] = existing_key
                return existing_node

        # 4. Create brand new canonical EntityNode
        new_node = EntityNode(
            id=str(uuid.uuid4()),
            canonical_name=canonical_name,
            entity_type=entity_type,
            aliases=[raw_name] if raw_name != canonical_name else [],
            mention_count=1,
            provenance_list=[provenance] if provenance else [],
            properties={}
        )

        self.entities_by_key[lookup_key] = new_node
        self.alias_to_key[raw_lower] = lookup_key
        self.alias_to_key[canonical_name.lower()] = lookup_key

        return new_node

    def _update_node(self, node: EntityNode, raw_name: str, provenance: Optional[GraphProvenance]) -> None:
        """Appends alias, increments count, and adds provenance citation."""
        node.mention_count += 1
        if raw_name != node.canonical_name and raw_name not in node.aliases:
            node.aliases.append(raw_name)
        if provenance:
            # Check for duplicate chunk provenance before adding
            if not any(p.chunk_id == provenance.chunk_id and p.exact_snippet == provenance.exact_snippet for p in node.provenance_list):
                node.provenance_list.append(provenance)

    def _is_fuzzy_match(self, key1: str, key2: str, name1: str, name2: str) -> bool:
        """Determines if two entity names refer to the same concept."""
        if not key1 or not key2:
            return False
        if key1 == key2:
            return True
        # If one is exact substring of another and length is close
        if len(key1) > 4 and len(key2) > 4:
            if key1.startswith(key2) or key2.startswith(key1):
                if abs(len(key1) - len(key2)) <= 3:
                    return True
        return False

    def get_all_entities(self) -> List[EntityNode]:
        """Returns list of all resolved canonical entities."""
        return list(self.entities_by_key.values())

    def clear(self) -> None:
        """Clears in-memory resolution cache."""
        self.entities_by_key.clear( )
        self.alias_to_key.clear()
