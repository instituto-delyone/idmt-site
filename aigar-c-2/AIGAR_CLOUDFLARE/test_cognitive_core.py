import unittest

from association_core import CognitiveContextCore


class CognitiveContextCoreTests(unittest.TestCase):
    def setUp(self):
        self.core = CognitiveContextCore()
        self.chunks = [
            {
                "id": "interaction-1",
                "source_key": "interacoes_aigar",
                "source": "Interações AIGAR",
                "sequence": 1,
                "text": "O AIGAR utiliza contexto, memória e diálogo para organizar interações.",
            },
            {
                "id": "math-1",
                "source_key": "matematica_computacional",
                "source": "Matemática computacional",
                "sequence": 1,
                "text": "A derivada de uma função representa sua taxa de variação instantânea.",
            },
            {
                "id": "ethics-1",
                "source_key": "etica",
                "source": "Ética",
                "sequence": 1,
                "text": "Responsabilidade e justiça são princípios relevantes para decisões éticas.",
            },
        ]

    def test_core_selects_context_before_answer_generation(self):
        context = self.core.prepare("Como calcular a derivada de uma função?", self.chunks)
        self.assertTrue(context["ready"])
        self.assertEqual(context["version"], "1.0.0")
        self.assertLessEqual(context["selected_count"], 3)
        self.assertIn("interaction-1", [item["chunk_id"] for item in context["selected_chunks"]])
        self.assertIn("math-1", [item["chunk_id"] for item in context["selected_chunks"]])

    def test_core_compiles_chunk_index_and_returns_source_excerpt(self):
        count = self.core.prime(self.chunks)
        self.assertEqual(count, 3)
        context = self.core.prepare("derivada função", self.chunks)
        math_chunk = next(item for item in context["selected_chunks"] if item["chunk_id"] == "math-1")
        self.assertIn("derivada", math_chunk["excerpt"].lower())
        self.assertLessEqual(len(math_chunk["excerpt"]), 1250)

    def test_annotation_preserves_original_interpretation(self):
        context = self.core.prepare("O que é derivada?", self.chunks)
        reading = {"intent": "concept_basic", "linguistic_analysis": {"analysis_status": "test"}}
        annotated = self.core.annotate_reading(reading, context)
        self.assertEqual(annotated["intent"], "concept_basic")
        self.assertTrue(annotated["linguistic_analysis"]["cognitive_core"]["ready"])
        self.assertEqual(reading["linguistic_analysis"]["analysis_status"], "test")


if __name__ == "__main__":
    unittest.main()
