"""
Structure-aware semantic chunking implementation.
Preserves page indices, section headers, character offsets, and sentence boundaries.
"""
from typing import List, Optional
import re
from app.domain.models import Document, DocumentChunk, ChunkSpan
from app.core.config import settings
from app.core.logging import logger


class SemanticChunker:
    """Chunks documents into semantically coherent windows with structural metadata."""

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        min_chunk_length: int = settings.MIN_CHUNK_LENGTH
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length

    def chunk(self, document: Document) -> List[DocumentChunk]:
        raw_text = document.content
        if not raw_text.strip():
            return []

        chunks: List[DocumentChunk] = []
        
        # Split text into structural blocks (paragraphs, headers, page markers)
        lines = raw_text.splitlines(keepends=True)
        
        current_page = 1
        current_section = "Introduction"
        current_buffer = ""
        buffer_start_char = 0
        global_char_offset = 0

        # Pre-process line boundaries
        for line in lines:
            line_len = len(line)
            stripped = line.strip()

            # Check for page markers from PDF parser
            page_match = re.match(r"<!-- PAGE_(\d+) -->", stripped)
            if page_match:
                new_page = int(page_match.group(1))
                if current_buffer.strip() and len(current_buffer.strip()) >= self.min_chunk_length:
                    chunk_id = f"{document.id}_chunk_{len(chunks)}"
                    chunk_text = current_buffer.strip()
                    chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            document_id=document.id,
                            chunk_index=len(chunks),
                            content=chunk_text,
                            span=ChunkSpan(
                                start_char=buffer_start_char,
                                end_char=buffer_start_char + len(current_buffer),
                                page_number=current_page,
                                section_title=current_section
                            ),
                            metadata={
                                "filename": document.filename,
                                "file_type": document.metadata.file_type,
                                "title": document.metadata.title or document.filename,
                                "page": current_page,
                                "section": current_section
                            },
                            token_count=len(chunk_text.split())
                        )
                    )
                    current_buffer = ""
                    buffer_start_char = global_char_offset
                current_page = new_page
                global_char_offset += line_len
                continue

            # Check for markdown headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if header_match:
                current_section = header_match.group(2).strip()

            # If adding this line exceeds chunk size and we have enough text
            if len(current_buffer) + line_len > self.chunk_size and len(current_buffer) >= self.min_chunk_length:
                # Emit chunk
                chunk_id = f"{document.id}_chunk_{len(chunks)}"
                chunk_text = current_buffer.strip()
                
                if len(chunk_text) >= self.min_chunk_length:
                    chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            document_id=document.id,
                            chunk_index=len(chunks),
                            content=chunk_text,
                            span=ChunkSpan(
                                start_char=buffer_start_char,
                                end_char=buffer_start_char + len(current_buffer),
                                page_number=current_page,
                                section_title=current_section
                            ),
                            metadata={
                                "filename": document.filename,
                                "file_type": document.metadata.file_type,
                                "title": document.metadata.title or document.filename,
                                "page": current_page,
                                "section": current_section
                            },
                            token_count=len(chunk_text.split())
                        )
                    )

                # Overlap: Keep the tail end of the buffer
                overlap_chars = self.chunk_overlap
                if len(current_buffer) > overlap_chars:
                    # Find a clean sentence or newline break in the overlap region
                    overlap_slice = current_buffer[-overlap_chars:]
                    break_idx = overlap_slice.rfind("\n")
                    if break_idx == -1:
                        break_idx = overlap_slice.rfind(". ")
                    
                    if break_idx != -1 and break_idx < len(overlap_slice) - 1:
                        keep_text = overlap_slice[break_idx + 1:]
                    else:
                        keep_text = overlap_slice
                    
                    buffer_start_char = global_char_offset - len(keep_text)
                    current_buffer = keep_text + line
                else:
                    buffer_start_char = global_char_offset
                    current_buffer = line
            else:
                if not current_buffer:
                    buffer_start_char = global_char_offset
                current_buffer += line

            global_char_offset += line_len

        # Flush remaining buffer
        if current_buffer.strip() and len(current_buffer.strip()) >= 20:
            chunk_id = f"{document.id}_chunk_{len(chunks)}"
            chunk_text = current_buffer.strip()
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    span=ChunkSpan(
                        start_char=buffer_start_char,
                        end_char=buffer_start_char + len(current_buffer),
                        page_number=current_page,
                        section_title=current_section
                    ),
                    metadata={
                        "filename": document.filename,
                        "file_type": document.metadata.file_type,
                        "title": document.metadata.title or document.filename,
                        "page": current_page,
                        "section": current_section
                    },
                    token_count=len(chunk_text.split())
                )
            )

        logger.info(f"Chunked document '{document.filename}' into {len(chunks)} semantic chunks.")
        return chunks
