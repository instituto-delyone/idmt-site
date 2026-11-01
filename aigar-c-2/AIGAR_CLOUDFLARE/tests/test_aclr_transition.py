import asyncio
import unittest
from aclr_transition import configured_aclr_mode, execute_aclr_transition, _adapt_evidence

class ACLRTransitionTests(unittest.TestCase):
    def test_default_mode_is_shadow(self):
        self.assertEqual(configured_aclr_mode(object()), "shadow")
    def test_unknown_mode_fails_closed(self):
        class Env: ACLR_MODE = "activate-everything"
        self.assertEqual(configured_aclr_mode(Env()), "shadow")
    def test_synthetic_sources_are_never_adapted(self):
        self.assertEqual(_adapt_evidence([{"evidence_id":"x","text":"synthetic","provenance":{"source_status":"synthetic_test_content"}}]), [])
    def test_verified_sources_are_mapped(self):
        items = _adapt_evidence([{"evidence_id":"chunk-1","source_id":"medicine","text":"Verified content","domain_ids":["medicine"],"provenance":{"source_status":"verified","r2_key":"real/chunk.md"}}])
        self.assertEqual(items[0]["text"], "Verified content")
        self.assertEqual(items[0]["source_key"], "aclr_r2_index_first")
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
