import unittest

from cortex_compat import (
    ALLOWED_DEPTHS,
    ALLOWED_INTENTS,
    CORTEX_COMPATIBILITY,
    build_routing_decision,
    normalize_reading,
)


class CortexCompatibilityTests(unittest.TestCase):
    def test_normalize_reading_preserves_worker_annotations(self):
        original = {
            "intent": "continuity",
            "depth": "technical",
            "confidence": 0.8,
            "linguistic_analysis": {"question": {"type": "definition"}},
            "worker_annotation": "preserve-me",
        }

        normalized = normalize_reading(original)

        self.assertIn(normalized["intent"], ALLOWED_INTENTS)
        self.assertIn(normalized["depth"], ALLOWED_DEPTHS)
        self.assertTrue(normalized["needs_memory"])
        self.assertAlmostEqual(normalized["uncertainty"], 0.2)
        self.assertEqual(normalized["worker_annotation"], "preserve-me")
        self.assertEqual(normalized["linguistic_analysis"], original["linguistic_analysis"])
        self.assertNotIn("needs_memory", original)

    def test_unknown_contract_values_degrade_to_safe_defaults(self):
        normalized = normalize_reading({
            "intent": "future_unimplemented_intent",
            "depth": "verbose",
            "confidence": 1.4,
            "linguistic_analysis": [],
        })

        self.assertEqual(normalized["intent"], "unknown")
        self.assertEqual(normalized["depth"], "normal")
        self.assertEqual(normalized["uncertainty"], 0.0)
        self.assertEqual(normalized["linguistic_analysis"], {})
        self.assertTrue(normalized["needs_reasoning"])

    def test_routing_is_explicit_and_does_not_claim_diagnosis_execution(self):
        reading = normalize_reading({
            "intent": "continuity",
            "needs_library": False,
            "needs_diagnosis": True,
        })
        route = build_routing_decision(
            reading,
            {"context_required": False, "research_required": True},
        )

        self.assertTrue(route["use_memory"])
        self.assertTrue(route["use_library"])
        self.assertTrue(route["use_diagnosis"])
        self.assertTrue(route["use_reasoning"])
        self.assertEqual(route["diagnosis_execution"], "not_connected")
        self.assertFalse(CORTEX_COMPATIBILITY["local_cortex_imported"])


if __name__ == "__main__":
    unittest.main()
