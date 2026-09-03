"""
Evidence Accumulator for Cross-Iteration Knowledge Retention in NEXUS-RAG (Phase 7).
Preserves, merges, and deduplicates retrieved evidence chunks across multiple recovery attempts without loss.
"""
from typing import List, Dict, Set
from app.domain.models import ScoredChunk
from app.core.logging import logger


class EvidenceAccumulator:
    """Merges candidate evidence chunks from successive retrieval attempts without discarding prior useful knowledge."""

    def accumulate(
        self,
        existing_chunks: List[ScoredChunk],
        new_chunks: List[ScoredChunk]
    ) -> List[ScoredChunk]:
        """
        Merges new chunks into existing pool, deduplicating by chunk ID and keeping highest score.
        """
        chunk_map: Dict[str, ScoredChunk] = {}

        # 1. Index existing chunks
        for sc in existing_chunks:
            chunk_map[sc.chunk.id] = sc

        # 2. Merge new chunks
        added_count = 0
        updated_count = 0
        for sc in new_chunks:
            cid = sc.chunk.id
            if cid in chunk_map:
                # Update score if higher in new retrieval
                if sc.final_score > chunk_map[cid].final_score:
                    chunk_map[cid].final_score = sc.final_score
                    updated_count += 1
            else:
                chunk_map[cid] = sc
                added_count += 1

        # 3. Sort by final score descending
        accumulated = sorted(chunk_map.values(), key=lambda x: x.final_score, reverse=True)

        logger.info(
            f"Evidence Accumulator: Merged {len(new_chunks)} chunks -> "
            f"{added_count} new, {updated_count} score updates (Total Accumulated: {len(accumulated)})"
        )
        return accumulated
