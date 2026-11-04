import unittest
from types import SimpleNamespace
from unittest.mock import patch

from telemetry_runtime import build_runtime_health


class RuntimeHealthTests(unittest.TestCase):
    def library(self):
        return SimpleNamespace(
            INDEX_CACHE=[{"source": {"key": "demo"}}], INDEX_CACHE_AT=990.0,
            LIBRARY_BOOT_CACHE={"chunk-1": {"text": "demo"}},
            LIBRARY_BOOT_STATUS=[{"status": "ready", "chunks_loaded": 1}], LIBRARY_BOOT_AT=995.0,
            TEXT_MATRIX_CACHE=[{"id": "TM-01"}], TEXT_MATRIX_AT=996.0,
            TEXT_MATRIX_FILES=[("TM-01", "one.md")],
            CHUNK_CACHE={"chunk-1": "demo"},
        )

    @patch("telemetry_runtime.time.time", return_value=1000.0)
    def test_reports_observed_counts_and_ages(self, _clock):
        env = SimpleNamespace(AIGAR_LIBRARY_BUCKET=object(), AIGAR_DB=object())
        memory_lab = SimpleNamespace(status={"ready": True})
        result = build_runtime_health(env, self.library(), memory_lab)
        self.assertEqual(result["schema_version"], "1.1")
        self.assertEqual(result["components"]["library_indexes"]["detail"]["cached_indexes"], 1)
        self.assertEqual(result["components"]["library_boot"]["detail"]["cached_chunks"], 1)
        self.assertEqual(result["components"]["library_boot"]["detail"]["cache_age_seconds"], 5.0)
        self.assertEqual(result["components"]["text_matrix"]["state"], "READY")
        self.assertEqual(result["components"]["storage"]["state"], "CONFIGURED")
        self.assertFalse(result["components"]["storage"]["detail"]["io_verified"])
        self.assertIsNone(result["resources"]["isolate_memory"]["value"])

    def test_memory_lab_uses_real_status_contract(self):
        result = build_runtime_health(SimpleNamespace(), self.library(),
                                      SimpleNamespace(status={"ready": True}))
        self.assertEqual(result["components"]["memory_lab"]["state"], "READY")

    def test_missing_or_partial_caches_are_not_ready(self):
        library = SimpleNamespace(
            INDEX_CACHE=None, INDEX_CACHE_AT=0, LIBRARY_BOOT_CACHE={"one": {}},
            LIBRARY_BOOT_STATUS=[{"status": "partial"}], LIBRARY_BOOT_AT=0,
            TEXT_MATRIX_CACHE=None, TEXT_MATRIX_AT=0, TEXT_MATRIX_FILES=[("one", "one.md")],
            CHUNK_CACHE={},
        )
        result = build_runtime_health(SimpleNamespace(), library)
        self.assertEqual(result["components"]["library_indexes"]["state"], "NOT_INITIALIZED")
        self.assertEqual(result["components"]["library_boot"]["state"], "PARTIAL")
        self.assertEqual(result["components"]["text_matrix"]["state"], "NOT_INITIALIZED")
        self.assertEqual(result["components"]["storage"]["state"], "NOT_CONFIGURED")
        self.assertEqual(result["resources"]["isolate_memory"]["status"], "not_exposed")


if __name__ == "__main__":
    unittest.main()
