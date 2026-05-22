"""Compatibility shim for peer review consumers expecting sync-style access."""

from __future__ import annotations

import asyncio

from app.services.verification.peer_review_service import PeerReviewService, peer_review_service as _async_peer_review_service


class _PeerReviewServiceCompat:
    def __init__(self, service: PeerReviewService):
        self._service = service

    def __getattr__(self, name: str):
        return getattr(self._service, name)

    def review(self, enriched_papers):
        coro = self._service.review(enriched_papers)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            result = asyncio.run(coro)
        else:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(coro)
            finally:
                loop.close()

        for paper in result.get("papers", []):
            quality_metrics = paper.get("quality_metrics", {})
            if "consensus_score" in quality_metrics and "consensus_score" not in paper:
                paper["consensus_score"] = quality_metrics["consensus_score"]
        return result


peer_review_service = _PeerReviewServiceCompat(_async_peer_review_service)

__all__ = ["PeerReviewService", "peer_review_service"]
