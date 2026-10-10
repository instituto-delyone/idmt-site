import unittest

from memory_lab.engine import DEFAULT_CONFIG, MemoryLab, _is_memory_document


class MemoryLabTests(unittest.TestCase):
    def test_readme_txt_is_not_memory_content(self):
        for path in (
            "memory_lab/memoria_imediata/README.txt",
            "memory_lab/memoria_curto_prazo/readme.TXT",
            "memory_lab/memoria_longo_prazo/README.txt",
        ):
            self.assertFalse(_is_memory_document(path), path)

    def test_real_txt_documents_are_discovered(self):
        self.assertTrue(_is_memory_document("memory_lab/memoria_imediata/nota.txt"))
        self.assertTrue(_is_memory_document("memory_lab/memoria_longo_prazo/referencia.TXT"))
        self.assertFalse(_is_memory_document("memory_lab/memoria_imediata/nota.md"))

    def test_boot_and_fallback_settings_are_supported(self):
        self.assertIn("immediate_boot_required", DEFAULT_CONFIG)
        self.assertIn("fallback_min_score", DEFAULT_CONFIG)

    def test_fallback_min_score_filters_weak_matches(self):
        lab = MemoryLab(fetcher=None, config={"fallback_min_score": 2})
        lab.documents["curto_prazo"] = [
            {"path": "weak.txt", "name": "weak.txt", "content": "memoria contexto"},
            {"path": "strong.txt", "name": "strong.txt", "content": "memoria contexto AIGAR contexto"},
        ]
        results = lab.retrieve("memoria", "curto_prazo")
        self.assertTrue(results)
        self.assertTrue(all(item["score"] >= 2 for item in results))

    def test_required_immediate_boot_default_is_enabled(self):
        self.assertTrue(DEFAULT_CONFIG["immediate_boot_required"])
        self.assertEqual(DEFAULT_CONFIG["fallback_min_score"], 1)


if __name__ == "__main__":
    unittest.main()
