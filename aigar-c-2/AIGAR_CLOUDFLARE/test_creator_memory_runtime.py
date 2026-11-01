import hashlib
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from creator_memory_runtime import _memory_search_text, _query_terms, search_creator_memory


class CreatorMemoryHelpersTests(unittest.TestCase):
    def test_query_terms_preserve_accented_words_and_drop_short_terms(self):
        self.assertEqual(_query_terms("memória clínica e APS"), {"memória", "clínica", "aps"})

    def test_nested_payload_is_searchable(self):
        value = _memory_search_text({"state": {"last_user_input": "continuidade do cuidado"}})
        self.assertIn("continuidade do cuidado", value)

    def test_depth_is_bounded(self):
        value = {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}
        self.assertNotIn("deep", _memory_search_text(value))


class FakeStatement:
    def __init__(self, db, sql):
        self.db, self.sql, self.params = db, sql, ()

    def bind(self, *params):
        self.params = params
        return self

    async def first(self):
        return {"name": "creator_memory_records"}

    async def all(self):
        self.db.query = self.sql
        self.db.params = self.params
        return SimpleNamespace(results=self.db.rows)


class FakeDB:
    def __init__(self, rows):
        self.rows, self.query, self.params = rows, "", ()

    def prepare(self, sql):
        return FakeStatement(self, sql)


class FakeObject:
    def __init__(self, raw):
        self.raw = raw

    async def text(self):
        return self.raw


class FakeBucket:
    def __init__(self, objects):
        self.objects = objects

    async def get(self, key):
        raw = self.objects.get(key)
        return FakeObject(raw) if raw is not None else None


class CreatorMemoryRetrievalTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_is_scoped_to_authenticated_importer_and_verifies_hash(self):
        payload = {"text": "história clínica longitudinal APS"}
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        rows = [
            SimpleNamespace(id="mine", r2_key="mine.json", sha256=digest,
                            size_bytes=len(raw), imported_at="2026-11-01",
                            imported_by="creator-1", status="stored"),
            SimpleNamespace(id="other", r2_key="other.json", sha256=digest,
                            size_bytes=len(raw), imported_at="2026-11-02",
                            imported_by="creator-2", status="stored"),
        ]
        db, bucket = FakeDB(rows), FakeBucket({"mine.json": raw, "other.json": raw})
        env = {"AIGAR_DB": db, "AIGAR_LIBRARY_BUCKET": bucket}
        status, result = await search_creator_memory(env, "história clínica", {"id": "creator-1"})
        self.assertEqual(status, 200)
        self.assertEqual([x["record"]["id"] for x in result["documents"]], ["mine"])
        self.assertEqual(db.params, ("creator-1",))
        self.assertEqual(result["documents"][0]["record"]["sha256"], digest)

    async def test_hash_mismatch_is_never_returned_as_evidence(self):
        rows = [SimpleNamespace(id="tampered", r2_key="tampered.json", sha256="0" * 64,
                                size_bytes=10, imported_at="2026-11-01",
                                imported_by="creator-1", status="stored")]
        db, bucket = FakeDB(rows), FakeBucket({"tampered.json": '{"text":"história clínica"}'})
        env = {"AIGAR_DB": db, "AIGAR_LIBRARY_BUCKET": bucket}
        status, result = await search_creator_memory(env, "história clínica", {"id": "creator-1"})
        self.assertEqual(status, 200)
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["integrity_failures"], ["tampered"])


if __name__ == "__main__":
    unittest.main()
