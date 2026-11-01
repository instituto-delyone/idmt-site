import asyncio
import json
import unittest

from aclr_r2_runtime import run_aclr_r2_shadow, ACLR_ROOT

MASTER = {
    "domains": [{
        "domain_id": "history", "label": "História",
        "index_path": "domains/history/index.json",
        "signals": ["história", "medieval"]
    }]
}
DOMAIN = {
    "domain_id": "history", "label": "História", "status": "prototype",
    "subdomains": [{
        "subdomain_id": "medieval_history", "label": "História Medieval",
        "signals": ["idade média", "medieval"], "chunks": ["hist-medieval-001"]
    }]
}
MANIFEST = {
    "manifest_version": "aclr-catalog-v1-prototype",
    "general_index": {"index_key": f"{ACLR_ROOT}/general/index.json", "version": "v1"}
}
CHUNK = """---
chunk_id: hist-medieval-001
domain_id: history
subdomain_id: medieval_history
content_type: synthetic_prototype
source_status: synthetic_test_content
---

História Medieval é um período de estudo histórico.
"""

class FakeObject:
    def __init__(self, value): self.value = value
    async def text(self): return self.value

class FakeBucket:
    def __init__(self):
        self.objects = {
            f"{ACLR_ROOT}/manifest.json": json.dumps(MANIFEST),
            f"{ACLR_ROOT}/router_index.json": json.dumps(MASTER),
            f"{ACLR_ROOT}/domains/history/index.json": json.dumps(DOMAIN),
            f"{ACLR_ROOT}/chunks/hist-medieval-001.md": CHUNK,
        }
        self.reads = []
    async def get(self, key):
        self.reads.append(key)
        value = self.objects.get(key)
        return FakeObject(value) if value is not None else None

class Env:
    def __init__(self, bucket): self.AIGAR_LIBRARY_BUCKET = bucket

class ACLRR2RuntimeTests(unittest.TestCase):
    def test_index_first_selects_only_referenced_chunk(self):
        bucket = FakeBucket()
        result = asyncio.run(run_aclr_r2_shadow(Env(bucket), "Explique a História Medieval"))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["selected_chunk_ids"], ["hist-medieval-001"])
        self.assertTrue(result["synthetic_only"])
        self.assertIn(f"{ACLR_ROOT}/chunks/hist-medieval-001.md", bucket.reads)
        self.assertNotIn(f"{ACLR_ROOT}/chunks/hist-ancient-001.md", bucket.reads)

    def test_missing_catalog_isolated(self):
        class EmptyBucket:
            async def get(self, key): return None
        result = asyncio.run(run_aclr_r2_shadow(Env(EmptyBucket()), "História Medieval"))
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "FileNotFoundError")

if __name__ == "__main__":
    unittest.main()
