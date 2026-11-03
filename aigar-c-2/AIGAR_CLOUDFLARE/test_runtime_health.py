import unittest
from types import SimpleNamespace

from telemetry_runtime import build_runtime_health


class RuntimeHealthTests(unittest.TestCase):
    def test_reports_cache_counts_and_age_without_triggering_boot(self):
        now = 1000.0
        library = SimpleNamespace(
            INDEX_CACHE=[{"source": {"key": "demo"}}],
            INDEX_CACHE_AT=990.0,
            LIBRARY_BOOT_CACHE={"chunk-1": {"text": "demo"}},
            LIBRARY_BOOT_STATUS=[{"chunks_loaded": 1}],
            LIBRARY_BOOT_AT=995.0,
            TEXT_MATRIX_CACHE=[{"id": "TM-01"}],
            TEXT_MATRIX_AT=996.0,
            TEXT_MATRIX_FILES=[("TM-01", "one.md")],
            CHUNK_CACHE={"chunk-1": "demo"},
        )
        env = SimpleNamespace(AIGAR_LIBRARY_BUCKET=object(), AIGAR_DB=object())
        memory_lab = SimpleNamespace(initialized=True)

        import telemetry_runtime
        original_time = telemetry_runtime.time.time
        telemetry_runtime.time.time = lambda: now
        try:
            result = build_runtime_health(env, library, memory_lab)
        finally:
            telemetry_runtime.time.time = original_time

        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["components"]["library_indexes"]["detail"]["cached_indexes"], 1)
        self.assertEqual(result["components"]["library_boot"]["detail"]["cached_chunks"], 1)
        self.assertEqual(result["components"]["library_boot"]["detail"]["cache_age_seconds"], 5.0)
        self.assertEqual(result["components"]["text_matrix"]["state"], "READY")
        self.assertEqual(result["components"]["storage"]["state"], "READY")
        self.assertIsNone(result["resources"]["isolate_memory"]["value"])

    def test_missing_caches_are_not_reported_as_ready(self):
        library = SimpleNamespace(
            INDEX_CACHE=None, INDEX_CACHE_AT=0,
            LIBRARY_BOOT_CACHE=None, LIBRARY_BOOT_STATUS=None, LIBRARY_BOOT_AT=0,
            TEXT_MATRIX_CACHE=None, TEXT_MATRIX_AT=0, TEXT_MATRIX_FILES=[],
            CHUNK_CACHE={},
        )
        env = SimpleNamespace()
        result = build_runtime_health(env, library)
        self.assertEqual(result["components"]["library_indexes"]["state"], "NOT_INITIALIZED")
        self.assertEqual(result["components"]["library_boot"]["state"], "NOT_INITIALIZED")
        self.assertEqual(result["components"]["text_matrix"]["state"], "NOT_INITIALIZED")
        self.assertEqual(result["resources"]["isolate_memory"]["status"], "not_exposed")


if __name__ == "__main__":
    unittest.main()
