"""
Multimodal Evidence Service for NEXUS-RAG (Phase 8).
Coordinates document representation hierarchy (Text, Tables, Figures, Images, Code, Metadata, References),
cross-modality retrieval, and strict provenance labeling.
"""
from typing import List, Dict, Any, Optional
import time
import uuid
import re
from app.domain.models import (
    Document,
    DocumentChunk,
    ModalityType,
    TableData,
    ChartFigureData,
    ImageData,
    CodeBlockData,
    MultimodalDocumentRepresentation,
    MultimodalEvidenceItem,
    MultimodalRetrievalResult,
    ScoredChunk,
    RetrievalMode
)
from app.services.retrieval_service import RetrievalService
from app.infrastructure.parsers.table_extractor import TableExtractor
from app.infrastructure.parsers.chart_figure_extractor import ChartFigureExtractor
from app.infrastructure.parsers.code_parser import CodeParser
from app.infrastructure.parsers.image_ocr_parser import ImageOCRParser
from app.infrastructure.llm.provider import get_llm_provider
from app.core.logging import logger


class MultimodalService:
    """Extracts, indexes, and retrieves structured multimodal evidence items with strict provenance."""

    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.table_extractor = TableExtractor()
        self.figure_extractor = ChartFigureExtractor()
        self.code_parser = CodeParser()
        self.image_parser = ImageOCRParser()
        self.llm_provider = get_llm_provider()

    def build_document_representation(
        self,
        document: Document,
        text_chunks: Optional[List[DocumentChunk]] = None
    ) -> MultimodalDocumentRepresentation:
        """
        Extracts and organizes the complete document representation hierarchy:
        Document -> Text | Tables | Figures | Images | Code | Metadata | References
        """
        content = document.content
        filename = document.filename
        doc_id = document.id

        # 1. Extract Tables
        if filename.endswith(".csv"):
            tables = [self.table_extractor.extract_from_csv(content, filename)]
        else:
            tables = self.table_extractor.extract_markdown_tables(content)

        # 2. Extract Figures & Charts
        figures = self.figure_extractor.extract_figures_and_charts(content)

        # 3. Extract Code Blocks
        code_blocks = self.code_parser.extract_code_blocks_from_markdown(content)
        if document.metadata.file_type.startswith("code_"):
            code_blocks.append(CodeBlockData(
                code_id=f"code-{uuid.uuid4().hex[:8]}",
                language=document.metadata.custom_attributes.get("language", "python"),
                code_content=content,
                source_file=filename,
                source_page=1
            ))

        # 4. Extract Images / OCR metadata
        images: List[ImageData] = []
        if document.metadata.file_type.startswith("image_"):
            images.append(ImageData(
                image_id=f"img-{uuid.uuid4().hex[:8]}",
                image_type=document.metadata.custom_attributes.get("image_type", "scan"),
                ocr_text=document.metadata.custom_attributes.get("ocr_text", content),
                caption=filename,
                source_page=1,
                image_format=document.metadata.custom_attributes.get("image_format", "png")
            ))


        # 5. Extract Document References
        references: List[str] = []
        ref_matches = re.findall(r"\[\d+\]\s+([^\n]{15,})", content)
        references.extend(ref_matches[:10])

        return MultimodalDocumentRepresentation(
            document_id=doc_id,
            filename=filename,
            text_chunks=text_chunks or [],
            tables=tables,
            figures=figures,
            images=images,
            code_blocks=code_blocks,
            metadata=document.metadata,
            references=references
        )

    def retrieve_multimodal_evidence(
        self,
        query: str,
        requested_modality: Optional[str] = None,
        top_k: int = 8
    ) -> MultimodalRetrievalResult:
        """
        Retrieves multimodal evidence items (Text, Tables, Figures, Images, Code) matching the query.
        """
        start_time = time.time()
        logger.info(f"Retrieving multimodal evidence for query: '{query}' (Modality Filter: {requested_modality or 'ALL'})")

        # 1. Retrieve ranked candidate chunks
        chunks, trace = self.retrieval_service.retrieve_with_trace(
            query=query,
            mode=RetrievalMode(top_k=top_k * 2)
        )

        evidence_items: List[MultimodalEvidenceItem] = []
        modality_counts: Dict[str, int] = {
            "text": 0,
            "table": 0,
            "figure": 0,
            "code": 0,
            "image": 0
        }

        query_lower = query.lower()

        for sc in chunks:
            chunk = sc.chunk
            fname = chunk.metadata.get("filename", "Doc")
            page = chunk.span.page_number if chunk.span else 1
            content = chunk.content

            # Check for Tables in chunk
            tables = self.table_extractor.extract_markdown_tables(content, default_page=page)
            if tables:
                for tbl in tables:
                    modality_counts["table"] += 1
                    evidence_items.append(MultimodalEvidenceItem(
                        evidence_id=f"evi-tbl-{uuid.uuid4().hex[:8]}",
                        modality=ModalityType.TABLE,
                        document_id=chunk.document_id,
                        document_filename=fname,
                        page_number=tbl.source_page or page,
                        title=tbl.caption or f"Table (Page {page})",
                        caption=tbl.caption,
                        content_snippet=tbl.markdown_repr[:200],
                        table_data=tbl,
                        relevance_score=round(sc.final_score * 1.15 if "table" in query_lower else sc.final_score, 3),
                        provenance_label=f"{tbl.caption or 'Table'} • {fname} • Page {tbl.source_page or page}"
                    ))

            # Check for Figures & Charts in chunk
            figures = self.figure_extractor.extract_figures_and_charts(content, default_page=page)
            if figures:
                for fig in figures:
                    modality_counts["figure"] += 1
                    evidence_items.append(MultimodalEvidenceItem(
                        evidence_id=f"evi-fig-{uuid.uuid4().hex[:8]}",
                        modality=ModalityType.FIGURE,
                        document_id=chunk.document_id,
                        document_filename=fname,
                        page_number=fig.source_page or page,
                        title=fig.title or fig.caption or f"Figure (Page {page})",
                        caption=fig.caption,
                        content_snippet=fig.explanatory_text or content[:200],
                        chart_data=fig,
                        relevance_score=round(sc.final_score * 1.15 if ("figure" in query_lower or "chart" in query_lower or "plot" in query_lower) else sc.final_score, 3),
                        provenance_label=f"{fig.caption or 'Figure'} • {fname} • Page {fig.source_page or page}"
                    ))

            # Check for Code Blocks in chunk
            code_blocks = self.code_parser.extract_code_blocks_from_markdown(content, default_page=page)
            if code_blocks or chunk.metadata.get("is_code"):
                for cb in code_blocks:
                    modality_counts["code"] += 1
                    evidence_items.append(MultimodalEvidenceItem(
                        evidence_id=f"evi-code-{uuid.uuid4().hex[:8]}",
                        modality=ModalityType.CODE,
                        document_id=chunk.document_id,
                        document_filename=fname,
                        page_number=cb.source_page or page,
                        title=f"Code Block ({cb.language})",
                        caption=f"Source Snippet ({cb.language})",
                        content_snippet=cb.code_content[:200],
                        code_data=cb,
                        relevance_score=round(sc.final_score * 1.15 if ("code" in query_lower or "implementation" in query_lower) else sc.final_score, 3),
                        provenance_label=f"Code ({cb.language.upper()}) • {fname} • Page {cb.source_page or page}"
                    ))

            # Check for Image / Scan
            if chunk.metadata.get("file_type", "").startswith("image_"):
                modality_counts["image"] += 1
                img_data = ImageData(
                    image_id=f"img-{uuid.uuid4().hex[:8]}",
                    image_type=chunk.metadata.get("image_type", "scan"),
                    ocr_text=content,
                    caption=fname,
                    source_page=page
                )
                evidence_items.append(MultimodalEvidenceItem(
                    evidence_id=f"evi-img-{uuid.uuid4().hex[:8]}",
                    modality=ModalityType.IMAGE,
                    document_id=chunk.document_id,
                    document_filename=fname,
                    page_number=page,
                    title=f"Image Scan ({fname})",
                    caption=f"OCR Visual Scan",
                    content_snippet=content[:200],
                    image_data=img_data,
                    relevance_score=round(sc.final_score, 3),
                    provenance_label=f"Image Scan • {fname} • Page {page}"
                ))

            # Add Text Modality Item
            modality_counts["text"] += 1
            evidence_items.append(MultimodalEvidenceItem(
                evidence_id=f"evi-txt-{uuid.uuid4().hex[:8]}",
                modality=ModalityType.TEXT,
                document_id=chunk.document_id,
                document_filename=fname,
                page_number=page,
                title=f"Text Passage (Page {page})",
                caption=chunk.span.section_title if chunk.span else None,
                content_snippet=content[:300],
                relevance_score=round(sc.final_score, 3),
                provenance_label=f"Text Passage • {fname} • Page {page}"
            ))

        # Filter by requested modality if specified
        if requested_modality and requested_modality != "all":
            req_mod = requested_modality.lower()
            if req_mod in ("table", "tables"):
                evidence_items = [e for e in evidence_items if e.modality == ModalityType.TABLE]
            elif req_mod in ("figure", "figures", "chart", "charts"):
                evidence_items = [e for e in evidence_items if e.modality in (ModalityType.FIGURE, ModalityType.CHART)]
            elif req_mod in ("code", "scripts"):
                evidence_items = [e for e in evidence_items if e.modality == ModalityType.CODE]
            elif req_mod in ("image", "images", "scan", "scans"):
                evidence_items = [e for e in evidence_items if e.modality == ModalityType.IMAGE]
            elif req_mod in ("text", "passages"):
                evidence_items = [e for e in evidence_items if e.modality == ModalityType.TEXT]

        # Deduplicate and sort by relevance score
        seen_snippets = set()
        deduped_items: List[MultimodalEvidenceItem] = []
        for item in sorted(evidence_items, key=lambda x: x.relevance_score, reverse=True):
            snip_key = f"{item.modality}:{item.document_filename}:{item.page_number}:{item.content_snippet[:50]}"
            if snip_key not in seen_snippets:
                seen_snippets.add(snip_key)
                deduped_items.append(item)

        top_evidence = deduped_items[:top_k]

        # Generate Multimodal Evidence Synthesis
        evidence_lines = []
        for e in top_evidence:
            evidence_lines.append(f"- **[{e.modality.value.upper()}]** {e.provenance_label}: {e.content_snippet[:120]}...")

        synthesis_md = (
            f"### Multimodal Evidence Intelligence Report\n\n"
            f"**Query**: *\"{query}\"*\n\n"
            f"Retrieved **{len(top_evidence)}** verified multimodal evidence item(s) across `{', '.join([k.upper() for k, v in modality_counts.items() if v > 0])}`.\n\n"
            f"#### Multimodal Citations & Provenance\n"
            + "\n".join(evidence_lines if evidence_lines else ["No multimodal evidence items found matching the query."])
        )

        exec_ms = round((time.time() - start_time) * 1000, 2)
        confidence = round(min(1.0, sum(e.relevance_score for e in top_evidence[:3]) / max(1, min(3, len(top_evidence)))), 2) if top_evidence else 0.0

        return MultimodalRetrievalResult(
            query=query,
            synthesis_markdown=synthesis_md,
            evidence_items=top_evidence,
            modality_counts=modality_counts,
            overall_confidence=confidence,
            execution_time_ms=exec_ms,
            model_used="multimodal_evidence_v1"
        )
