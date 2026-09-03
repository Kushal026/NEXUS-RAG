"""
Relationship Extractor for NEXUS-RAG Knowledge Graph Intelligence (Phase 5).
Extracts typed directional relationships between resolved entities with strict chunk-level provenance.
"""
from typing import List, Dict, Any, Tuple, Optional, Set
import re
import uuid
from app.domain.models import (
    EntityNode,
    EntityType,
    RelationshipType,
    RelationshipEdge,
    GraphProvenance,
    DocumentChunk
)
from app.core.logging import logger


class RelationshipExtractor:
    """Extracts verified typed semantic relationships connecting entities in document chunks."""

    # Explicit relational phrase patterns
    PATTERNS: List[Tuple[RelationshipType, List[str]]] = [
        (
            RelationshipType.AUTHORED_BY,
            [
                r"(?:written|authored|published|presented|proposed)\s+by",
                r"authors?(?:\s+include|:\s*|\s+are)",
                r"by\s+(?:the\s+authors?|researchers?)"
            ]
        ),
        (
            RelationshipType.CREATED_BY,
            [
                r"(?:developed|created|built|designed|invented|released|engineered)\s+by",
                r"(?:is|was)\s+a\s+(?:product|model|system|platform)\s+(?:of|from|by)",
                r"(?:by\s+the\s+team\s+at|by\s+researchers\s+at)"
            ]
        ),
        (
            RelationshipType.INTRODUCED,
            [
                r"(?:introduced|presented|proposed|first\s+described|unveiled)\s+(?:in|by|the)",
                r"introduced\s+the\s+concept\s+of"
            ]
        ),
        (
            RelationshipType.USES,
            [
                r"(?:uses|utilizes|leverages|incorporates|employs|relies\s+on|integrates)\b",
                r"(?:is\s+based\s+on|built\s+on\s+top\s+of|powered\s+by)",
                r"(?:adopted|implements|takes\s+advantage\s+of)"
            ]
        ),
        (
            RelationshipType.DEPENDS_ON,
            [
                r"(?:depends\s+on|is\s+dependent\s+on|requires|relies\s+strictly\s+on)\b",
                r"(?:prerequisite|built\s+upon)"
            ]
        ),
        (
            RelationshipType.EVALUATED_ON,
            [
                r"(?:evaluated|tested|benchmarked|measured|validated)\s+on\b",
                r"(?:performance|results|accuracy|score)\s+on\s+(?:the\s+)?",
                r"(?:benchmark|dataset)\s+such\s+as"
            ]
        ),
        (
            RelationshipType.COMPETES_WITH,
            [
                r"(?:compared\s+with|compared\s+to|outperforms|rivals|competitor\s+to|versus|vs\.?)\b",
                r"(?:alternative\s+to|supersedes|benchmarked\s+against)"
            ]
        ),
        (
            RelationshipType.AFFILIATED_WITH,
            [
                r"(?:researcher\s+at|engineer\s+at|founder\s+of|ceo\s+of|works?\s+at|affiliated\s+with|at\s+Google|at\s+OpenAI|at\s+DeepMind|at\s+Meta)\b"
            ]
        ),
        (
            RelationshipType.TRAINED_ON,
            [
                r"(?:trained\s+on|fine-tuned\s+on|pre-trained\s+on|trained\s+using\s+the)\b"
            ]
        ),
        (
            RelationshipType.SUCCEEDED_BY,
            [
                r"(?:succeeded\s+by|followed\s+by|improved\s+upon\s+by|later\s+replaced\s+by)\b"
            ]
        ),
        (
            RelationshipType.PRECEDED_BY,
            [
                r"(?:preceded\s+by|building\s+on\s+prior\s+work\s+by|earlier\s+work\s+by)\b"
            ]
        ),
    ]

    def extract_relationships_from_chunk(
        self,
        chunk: DocumentChunk,
        entities: List[EntityNode]
    ) -> List[RelationshipEdge]:
        """
        Extracts verified relationships among entities occurring in the given chunk text.
        Every relationship edge stores full provenance (document, page, chunk, snippet).
        """
        if len(entities) < 2:
            return []

        text = chunk.content
        fname = chunk.metadata.get("filename", "Unknown Document")
        page_num = chunk.span.page_number if chunk.span else None
        section = chunk.span.section_title if chunk.span else None

        edges: List[RelationshipEdge] = []
        seen_pairs: Set[Tuple[str, str, str]] = set()

        # Split chunk into sentences to evaluate co-occurrence within sentence or adjacent context
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sent in sentences:
            if len(sent.strip()) < 10:
                continue

            # Find all entities mentioned in this sentence
            present_entities: List[EntityNode] = []
            for ent in entities:
                # Check canonical name or any alias
                names_to_check = [ent.canonical_name] + ent.aliases
                for name in names_to_check:
                    if re.search(r"\b" + re.escape(name) + r"\b", sent, re.IGNORECASE):
                        if ent not in present_entities:
                            present_entities.append(ent)
                        break

            if len(present_entities) >= 2:
                # Pairwise relationship inspection
                for i in range(len(present_entities)):
                    for j in range(len(present_entities)):
                        if i == j:
                            continue
                        e1 = present_entities[i]
                        e2 = present_entities[j]

                        detected_rel, confidence, desc = self._detect_relation(sent, e1, e2)
                        
                        if detected_rel is not None:
                            pair_key = (e1.id, e2.id, detected_rel.value)
                            if pair_key in seen_pairs:
                                continue
                            seen_pairs.add(pair_key)

                            prov = GraphProvenance(
                                document_id=chunk.document_id,
                                document_filename=fname,
                                chunk_id=chunk.id,
                                page_number=page_num,
                                section_title=section,
                                exact_snippet=sent.strip(),
                                confidence=confidence
                            )

                            edge = RelationshipEdge(
                                id=str(uuid.uuid4()),
                                source_id=e1.id,
                                source_name=e1.canonical_name,
                                target_id=e2.id,
                                target_name=e2.canonical_name,
                                relationship_type=detected_rel,
                                description=desc or f"{e1.canonical_name} {detected_rel.value} {e2.canonical_name}",
                                weight=confidence,
                                provenance_list=[prov],
                                properties={"sentence": sent.strip()}
                            )
                            edges.append(edge)

        return edges

    def _detect_relation(
        self,
        sentence: str,
        e1: EntityNode,
        e2: EntityNode
    ) -> Tuple[Optional[RelationshipType], float, Optional[str]]:
        """
        Determines the directional typed relationship between e1 and e2 within a sentence.
        """
        # Find indices of entity mentions in sentence
        e1_match = re.search(r"\b" + re.escape(e1.canonical_name) + r"\b", sentence, re.IGNORECASE)
        e2_match = re.search(r"\b" + re.escape(e2.canonical_name) + r"\b", sentence, re.IGNORECASE)

        if not e1_match or not e2_match:
            return None, 0.0, None

        e1_pos = e1_match.start()
        e2_pos = e2_match.start()

        # Text spanning between or around the two entities
        start_idx = min(e1_pos, e2_pos)
        end_idx = max(e1_match.end(), e2_match.end())
        between_text = sentence[start_idx:end_idx]

        # 1. Check explicit pattern rules
        for rel_type, pattern_list in self.PATTERNS:
            for pat in pattern_list:
                if re.search(pat, sentence, re.IGNORECASE):
                    # Check directionality heuristics
                    if rel_type in (RelationshipType.AUTHORED_BY, RelationshipType.CREATED_BY, RelationshipType.AFFILIATED_WITH):
                        # E.g. Paper AUTHORED_BY Person, or Model CREATED_BY Company
                        if e1.entity_type in (EntityType.PAPER, EntityType.MODEL, EntityType.TECHNOLOGY) and e2.entity_type in (EntityType.PERSON, EntityType.ORGANIZATION, EntityType.COMPANY):
                            return rel_type, 0.95, f"{e1.canonical_name} is created/authored by {e2.canonical_name}"
                        elif e1.entity_type == EntityType.PERSON and e2.entity_type in (EntityType.ORGANIZATION, EntityType.COMPANY):
                            return RelationshipType.AFFILIATED_WITH, 0.90, f"{e1.canonical_name} is affiliated with {e2.canonical_name}"
                    
                    if rel_type == RelationshipType.EVALUATED_ON:
                        if e1.entity_type in (EntityType.MODEL, EntityType.TECHNOLOGY) and e2.entity_type in (EntityType.DATASET, EntityType.CONCEPT):
                            return rel_type, 0.92, f"{e1.canonical_name} evaluated on {e2.canonical_name}"

                    if rel_type in (RelationshipType.USES, RelationshipType.DEPENDS_ON):
                        if e1_pos < e2_pos:
                            return rel_type, 0.88, f"{e1.canonical_name} utilizes {e2.canonical_name}"

                    if rel_type == RelationshipType.COMPETES_WITH:
                        return rel_type, 0.85, f"{e1.canonical_name} is compared with or competes with {e2.canonical_name}"

        # 2. Domain Taxonomy Fallback: Type-driven default relationships
        if e1.entity_type == EntityType.PAPER and e2.entity_type == EntityType.PERSON:
            return RelationshipType.AUTHORED_BY, 0.80, f"{e1.canonical_name} authored by {e2.canonical_name}"
        if e1.entity_type == EntityType.MODEL and e2.entity_type in (EntityType.ORGANIZATION, EntityType.COMPANY):
            return RelationshipType.CREATED_BY, 0.85, f"{e1.canonical_name} created by {e2.canonical_name}"
        if e1.entity_type == EntityType.PERSON and e2.entity_type in (EntityType.ORGANIZATION, EntityType.COMPANY):
            return RelationshipType.AFFILIATED_WITH, 0.80, f"{e1.canonical_name} affiliated with {e2.canonical_name}"
        if e1.entity_type in (EntityType.MODEL, EntityType.TECHNOLOGY) and e2.entity_type == EntityType.DATASET:
            return RelationshipType.EVALUATED_ON, 0.80, f"{e1.canonical_name} evaluated on {e2.canonical_name}"

        # 3. Contextual co-occurrence fallback if in immediate proximity (<100 chars)
        if len(between_text) < 120 and e1_pos < e2_pos:
            return RelationshipType.RELATED_TO, 0.65, f"{e1.canonical_name} is mentioned alongside {e2.canonical_name}"

        return None, 0.0, None
