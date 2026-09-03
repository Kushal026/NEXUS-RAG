"""
Entity Extractor for NEXUS-RAG Knowledge Graph Intelligence (Phase 5).
Extracts configurable typed entities from document chunks with character spans and strict provenance.
"""
from typing import List, Dict, Any, Tuple, Optional, Set
import re
from app.domain.models import EntityType, EntityNode, GraphProvenance, DocumentChunk
from app.core.logging import logger


class EntityExtractor:
    """Multi-layer entity extraction engine supporting configurable domain taxonomies."""

    # Built-in high-precision taxonomy recognition rules
    ORGANIZATION_PATTERNS = [
        r"\b(?:OpenAI|DeepMind|Google(?:\s+DeepMind|\s+Research)?|Microsoft|Meta(?:\s+AI)?|Anthropic|NVIDIA|Amazon|Apple|IBM|Baidu|Alibaba|Mistral(?:\s+AI)?|Cohere|Hugging\s*Face)\b(?:\s+(?:Inc\.?|LLC|Corp\.?|Corporation|Ltd\.?))?",
        r"\b(?:Stanford(?:\s+University)?|MIT|Harvard|UC\s+Berkeley|Carnegie\s+Mellon(?:\s+University)?|Oxford|Cambridge)\b"
    ]

    MODEL_PATTERNS = [
        r"\b(?:GPT-[345o]+(?:-mini|-turbo|-preview)?|ChatGPT|Claude(?:\s+[23]\.?[0-9]*)?(?:\s+(?:Sonnet|Opus|Haiku))?|Gemini(?:\s+[12]\.?[0-9]*)?(?:\s+(?:Ultra|Pro|Flash))?|LLaMA(?:\s*-[1234])?|BERT(?:-Large|-Base)?|RoBERTa|T5|PaLM(?:\s*2)?|Mistral-7B|Mixtral(?:\s*8x[0-9]+B)?|DeepSeek(?:\s*-[VR][0-9]+)?|Falcon|Vicuna|Whisper|DALL-E(?:\s*[23])?|Stable\s+Diffusion)\b",
        r"\b(?:all-MiniLM-L6-v2|bge-(?:small|base|large)-en|text-embedding-3-(?:small|large))\b"
    ]

    TECHNOLOGY_PATTERNS = [
        r"\b(?:Transformer|Self-Attention|Multi-Head\s+Attention|Feed-Forward\s+Network|Residual\s+Connection|Layer\s+Normalization|Vector\s+Database|Knowledge\s+Graph|Neo4j|PostgreSQL|pgvector|BM25|Cross-Encoder|Bi-Encoder|PyTorch|TensorFlow|JAX|Hugging\s*Face\s+Transformers|LangChain|LlamaIndex|FAISS|ChromaDB|Qdrant|Milvus|Redis)\b",
        r"\b(?:RAG|Hybrid\s+RAG|Retrieval-Augmented\s+Generation|Reciprocal\s+Rank\s+Fusion|RRF|Dense\s+Retrieval|Sparse\s+Retrieval)\b"
    ]

    DATASET_PATTERNS = [
        r"\b(?:MS\s+MARCO|SQuAD(?:\s*v?[12]\.0)?|GLUE|SuperGLUE|ImageNet|HotpotQA|BEIR|TriviaQA|Natural\s+Questions|MMLU|GSM8K|HumanEval|Common\s+Crawl|C4|Pile|RedPajama)\b"
    ]

    CONCEPT_PATTERNS = [
        r"\b(?:Semantic\s+Search|Cosine\s+Similarity|Vector\s+Embedding|Tokenization|Positional\s+Encoding|Attention\s+Mechanism|Fine-Tuning|Prompt\s+Engineering|Zero-Shot|Few-Shot|Chain-of-Thought|Graph\s+Traversal|Entity\s+Resolution|Provenance\s+Tracking|Temporal\s+Reasoning|Hallucination\s+Mitigation)\b"
    ]

    PERSON_PATTERNS = [
        r"\b(?:Ashish\s+Vaswani|Noam\s+Shazeer|Niki\s+Parmar|Jakob\s+Uszkoreit|Llion\s+Jones|Aidan\s+N\.\s+Gomez|Lukasz\s+Kaiser|Illia\s+Polosukhin)\b",
        r"\b(?:Geoffrey\s+Hinton|Yann\s+LeCun|Yoshua\s+Bengio|Demis\s+Hassabis|Ilya\s+Sutskever|Sam\s+Altman|Andrej\s+Karpathy|Dario\s+Amodei|Mira\s+Murati|Jensen\s+Huang)\b",
        r"\b(?:Kushal\s+H|Kushal)\b"
    ]

    PAPER_PATTERNS = [
        r"[\"“']Attention\s+Is\s+All\s+You\s+Need[\"”']|\bAttention\s+Is\s+All\s+You\s+Need\b",
        r"[\"“']Language\s+Models\s+are\s+Few-Shot\s+Learners[\"”']|\bLanguage\s+Models\s+are\s+Few-Shot\s+Learners\b",
        r"[\"“']Deep\s+Residual\s+Learning\s+for\s+Image\s+Recognition[\"”']",
        r"[\"“']Retrieval-Augmented\s+Generation\s+for\s+Knowledge-Intensive\s+NLP\s+Tasks[\"”']"
    ]

    DATE_PATTERNS = [
        r"\b(?:19\d{2}|20\d{2})(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?)?\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b"
    ]

    def __init__(self, custom_taxonomies: Optional[Dict[EntityType, List[str]]] = None):
        self.custom_taxonomies = custom_taxonomies or {}

    def extract_from_chunk(self, chunk: DocumentChunk) -> List[Tuple[str, EntityType, GraphProvenance]]:
        """
        Extracts entities from a single DocumentChunk.
        Returns tuples of (raw_entity_name, EntityType, GraphProvenance).
        """
        text = chunk.content
        fname = chunk.metadata.get("filename", "Unknown Document")
        page_num = chunk.span.page_number if chunk.span else None
        section = chunk.span.section_title if chunk.span else None
        
        extracted: List[Tuple[str, EntityType, GraphProvenance]] = []
        seen_spans: Set[Tuple[int, int]] = set()

        def _scan_patterns(patterns: List[str], ent_type: EntityType, default_conf: float = 0.95):
            for pat in patterns:
                for match in re.finditer(pat, text, re.IGNORECASE):
                    start, end = match.span()
                    # Prevent exact duplicate span overlapping
                    if any(s <= start and end <= e for (s, e) in seen_spans):
                        continue
                    seen_spans.add((start, end))

                    matched_text = match.group(0).strip(" \"'“”,.")
                    if len(matched_text) < 2:
                        continue

                    # Extract local snippet for provenance (e.g. 100 chars around match)
                    snip_start = max(0, start - 40)
                    snip_end = min(len(text), end + 40)
                    exact_snippet = text[snip_start:snip_end].strip()

                    prov = GraphProvenance(
                        document_id=chunk.document_id,
                        document_filename=fname,
                        chunk_id=chunk.id,
                        page_number=page_num,
                        section_title=section,
                        exact_snippet=exact_snippet,
                        confidence=default_conf
                    )
                    extracted.append((matched_text, ent_type, prov))

        # Run extraction across standard configurable taxonomies
        _scan_patterns(self.PAPER_PATTERNS, EntityType.PAPER, 0.98)
        _scan_patterns(self.PERSON_PATTERNS, EntityType.PERSON, 0.95)
        _scan_patterns(self.ORGANIZATION_PATTERNS, EntityType.ORGANIZATION, 0.95)
        _scan_patterns(self.MODEL_PATTERNS, EntityType.MODEL, 0.95)
        _scan_patterns(self.DATASET_PATTERNS, EntityType.DATASET, 0.90)
        _scan_patterns(self.TECHNOLOGY_PATTERNS, EntityType.TECHNOLOGY, 0.92)
        _scan_patterns(self.CONCEPT_PATTERNS, EntityType.CONCEPT, 0.88)
        _scan_patterns(self.DATE_PATTERNS, EntityType.DATE, 0.85)

        # Capitalized multi-word noun phrase heuristics for domain concepts
        cap_pattern = r"\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){1,3}\b"
        for match in re.finditer(cap_pattern, text):
            start, end = match.span()
            if any(s <= start and end <= e for (s, e) in seen_spans):
                continue
            matched_text = match.group(0).strip(" \"'“”,.")
            if len(matched_text.split()) > 1 and len(matched_text) > 4:
                # Filter common stop phrases
                if matched_text.lower() in {"in order", "on the", "as well", "this paper", "the proposed", "for example"}:
                    continue
                seen_spans.add((start, end))
                snip_start = max(0, start - 40)
                snip_end = min(len(text), end + 40)
                prov = GraphProvenance(
                    document_id=chunk.document_id,
                    document_filename=fname,
                    chunk_id=chunk.id,
                    page_number=page_num,
                    section_title=section,
                    exact_snippet=text[snip_start:snip_end].strip(),
                    confidence=0.75
                )
                extracted.append((matched_text, EntityType.CONCEPT, prov))

        return extracted

    def extract_from_text(self, text: str, document_id: str = "adhoc", filename: str = "Text Input") -> List[Tuple[str, EntityType, GraphProvenance]]:
        """Convenience method for ad-hoc text without a pre-constructed DocumentChunk."""
        chunk = DocumentChunk(
            id="adhoc-chunk",
            document_id=document_id,
            chunk_index=0,
            content=text,
            span={"start_char": 0, "end_char": len(text)},
            metadata={"filename": filename}
        )
        return self.extract_from_chunk(chunk)
