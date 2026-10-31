import unittest

from memory_card_runtime import MemoryCardAdapter, _safe_card_path


class FakeResponse:
    def __init__(self, text, status=200):
        self._text = text
        self.status = status

    async def text(self):
        return self._text


class MemoryCardAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_manifest_keeps_public_memory_optional(self):
        adapter = MemoryCardAdapter(manifest={
            "schema_version": "1.0",
            "manifest_id": "test",
            "cards": [],
        })
        result = await adapter.retrieve("AIGAR architecture")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["documents"], [])

    async def test_only_explicitly_public_cards_are_retrieved(self):
        card = "id: PUBLIC-CORE\nversion: '1.2'\n\nAIGAR architecture reasoning engine."
        calls = []

        async def fake_fetch(url, options=None):
            calls.append(url)
            return FakeResponse(card)

        adapter = MemoryCardAdapter(
            fetcher=fake_fetch,
            manifest={
                "schema_version": "1.0",
                "manifest_id": "test",
                "cards": [
                    {
                        "id": "PUBLIC-CORE", "version": "1.2",
                        "path": "aigar-c-2/public_cards/core.yaml",
                        "visibility": "public", "status": "active",
                    },
                    {
                        "id": "PRIVATE-USER", "version": "1.0",
                        "path": "aigar-c-2/private/user.yaml",
                        "visibility": "private", "status": "active",
                    },
                ],
            },
        )
        result = await adapter.retrieve("AIGAR architecture")

        self.assertEqual(result["status"], "ready")
        self.assertEqual(len(result["documents"]), 1)
        self.assertEqual(result["documents"][0]["memory_card_id"], "PUBLIC-CORE")
        self.assertEqual(result["documents"][0]["memory_card_version"], "1.2")
        self.assertEqual(len(calls), 1)
        self.assertIn("public_cards/core.yaml", calls[0])

    async def test_manifest_id_or_version_mismatch_is_rejected(self):
        async def fake_fetch(url, options=None):
            return FakeResponse("id: DIFFERENT\nversion: '1.2'\nAIGAR reasoning")

        adapter = MemoryCardAdapter(
            fetcher=fake_fetch,
            manifest={
                "schema_version": "1.0",
                "manifest_id": "test",
                "cards": [{
                    "id": "EXPECTED", "version": "1.2",
                    "path": "aigar-c-2/public_cards/core.yaml",
                    "visibility": "public", "status": "active",
                }],
            },
        )
        result = await adapter.retrieve("AIGAR reasoning")
        self.assertEqual(result["documents"], [])

    def test_paths_are_confined_to_repository_tree(self):
        self.assertIsNotNone(_safe_card_path("aigar-c-2/public_cards/core.yaml"))
        self.assertIsNone(_safe_card_path("../../secrets.yaml"))
        self.assertIsNone(_safe_card_path("outside/private.yaml"))
        self.assertIsNone(_safe_card_path("aigar-c-2/public_cards/core.exe"))


if __name__ == "__main__":
    unittest.main()
