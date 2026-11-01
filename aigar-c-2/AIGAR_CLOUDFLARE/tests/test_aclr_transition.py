import asyncio
import unittest
from unittest.mock import patch
from aclr_transition import configured_aclr_mode, execute_aclr_transition, _adapt_evidence

class ACLRTransitionTests(unittest.TestCase):
    def test_default_mode_is_shadow(self):
        self.assertEqual(configured_aclr_mode(object()), "shadow")
    def test_unknown_mode_fails_closed(self):
        class Env: ACLR_MODE = "activate-everything"
        self.assertEqual(configured_aclr_mode(Env()), "shadow")
    def test_synthetic_sources_are_never_adapted(self):
        self.assertEqual(_adapt_evidence([{"evidence_id":"x","text":"synthetic","provenance":{"source_status":"synthetic_test_content"}}]), [])
    def test_reviewed_sources_are_eligible(self):
        items = _adapt_evidence([{
            "evidence_id": "reviewed-1",
            "source_id": "reviewed-source",
            "text": "Reviewed content",
            "provenance": {"source_status": "reviewed"},
        }])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "Reviewed content")

    def test_verified_sources_are_mapped(self):
        items = _adapt_evidence([{"evidence_id":"chunk-1","source_id":"medicine","text":"Verified content","domain_ids":["medicine"],"provenance":{"source_status":"verified","r2_key":"real/chunk.md"}}])
        self.assertEqual(items[0]["text"], "Verified content")
        self.assertEqual(items[0]["source_key"], "aclr_r2_index_first")
    def test_explicit_candidate_override_is_available_for_shadow_lab(self):
        legacy = []
        class Env:
            ACLR_MODE = "shadow"
            AIGAR_LIBRARY_BUCKET = None
        async def fake_shadow(env, question, top_k=5):
            return {
                "status": "complete",
                "manifest_version": "test-v1",
                "planner_version": "test-planner",
                "selected_chunk_count": 1,
                "latency_ms": 3,
                "warnings": [],
                "source_statuses": ["verified"],
                "evidence_items": [{
                    "evidence_id": "verified-1",
                    "source_id": "verified-source",
                    "text": "Verified evidence",
                    "domain_ids": ["history"],
                    "provenance": {"source_status": "verified", "r2_key": "chunks/verified-1.md"},
                }],
            }
        with patch("aclr_transition.run_aclr_r2_shadow", new=fake_shadow):
            result = asyncio.run(execute_aclr_transition(
                Env(), "question", legacy, mode_override="candidate"
            ))
        self.assertEqual(result["diagnostic"]["mode"], "candidate")
        self.assertEqual(result["diagnostic"]["status"], "candidate_selected")
        self.assertEqual(result["evidence_items"][0]["text"], "Verified evidence")

    def test_invalid_mode_override_fails_closed_to_shadow(self):
        legacy = [{"text": "legacy"}]
        class Env:
            ACLR_MODE = "candidate"
            AIGAR_LIBRARY_BUCKET = None
        async def fake_shadow(env, question, top_k=5):
            return {"status": "complete", "evidence_items": []}
        with patch("aclr_transition.run_aclr_r2_shadow", new=fake_shadow):
            result = asyncio.run(execute_aclr_transition(
                Env(), "question", legacy, mode_override="unexpected"
            ))
        self.assertEqual(result["diagnostic"]["mode"], "shadow")
        self.assertEqual(result["evidence_items"], legacy)

    def test_shadow_keeps_legacy_evidence(self):
        legacy = [{"text":"legacy"}]
        class EmptyEnv:
            ACLR_MODE = "shadow"
            AIGAR_LIBRARY_BUCKET = None
        result = asyncio.run(execute_aclr_transition(EmptyEnv(), "question", legacy))
        self.assertEqual(result["evidence_items"], legacy)
        self.assertEqual(result["diagnostic"]["mode"], "shadow")

if __name__ == "__main__":
    unittest.main()
