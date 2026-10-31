import unittest

from cortex_compat import (
    ALLOWED_DEPTHS,
    ALLOWED_INTENTS,
    CORTEX_COMPATIBILITY,
    PUBLIC_CONVERSATION_POLICY,
    build_routing_decision,
    normalize_reading,
    WORKER_CORTEX_BRIDGE,
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
        self.assertIn("public_memory_card_adapter_allowlisted", CORTEX_COMPATIBILITY["implemented_capabilities"])
        self.assertIn("persistent_cross_instance_conversation_memory", CORTEX_COMPATIBILITY["deferred_capabilities"])
        self.assertEqual(CORTEX_COMPATIBILITY["access_policy"], PUBLIC_CONVERSATION_POLICY)
        self.assertFalse(PUBLIC_CONVERSATION_POLICY["identity_verification_required"])
        self.assertFalse(PUBLIC_CONVERSATION_POLICY["activation_phrase_required"])
        self.assertFalse(PUBLIC_CONVERSATION_POLICY["designated_email_required"])

    def test_worker_bridge_returns_canonical_reading_and_explicit_routing(self):
        result = WORKER_CORTEX_BRIDGE.interpret_contract(
            {
                "intent": "continuity",
                "scope": "decisão anterior",
                "ambiguity": 0.35,
                "confidence": 0.7,
                "needs_library": True,
                "linguistic_analysis": {"reference": "previous_decision"},
            },
            {"context_required": True, "research_required": False},
        )

        self.assertEqual(result["reading"]["scope"], "decisão anterior")
        self.assertAlmostEqual(result["reading"]["ambiguity"], 0.35)
        self.assertAlmostEqual(result["reading"]["uncertainty"], 0.3)
        self.assertTrue(result["routing_decision"]["use_memory"])
        self.assertTrue(result["routing_decision"]["use_library"])
        self.assertEqual(
            result["compatibility"]["routing_decision"],
            result["routing_decision"],
        )
        self.assertFalse(result["compatibility"]["local_cortex_imported"])
        self.assertEqual(result["routing_decision"]["conversation_access"], "public")
        self.assertFalse(result["routing_decision"]["identity_verification_required"])
        self.assertFalse(result["routing_decision"]["activation_phrase_required"])
        self.assertEqual(result["routing_decision"]["admin_authorization"], "separate_authenticated_admin_routes")


    def test_meta_interaction_routes_to_memory_without_identity_checks(self):
        result = WORKER_CORTEX_BRIDGE.interpret_contract(
            {"intent": "concept_basic", "needs_memory": False},
            {"primary_type": "meta_interaction", "context_required": False},
        )
        self.assertTrue(result["routing_decision"]["use_memory"])
        self.assertEqual(result["routing_decision"]["conversation_access"], "public")
        self.assertFalse(result["routing_decision"]["identity_verification_required"])


if __name__ == "__main__":
    unittest.main()
