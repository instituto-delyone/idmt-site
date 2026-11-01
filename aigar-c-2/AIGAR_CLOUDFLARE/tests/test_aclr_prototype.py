import unittest

from aclr_router import build_retrieval_plan, inspect_selected_targets
from aclr_contracts import ContractError, validate_query_request, validate_context_pointer
from aclr_resolver import resolve_evidence

MASTER = {
    "domains": [
        {"domain_id":"history","signals":["história","medieval","revolução industrial"],"status":"prototype"},
        {"domain_id":"mathematics","signals":["matemática","álgebra","geometria","cálculo"],"status":"prototype"},
        {"domain_id":"portuguese","signals":["português","gramática","morfologia","sintaxe","semântica","pragmática"],"status":"prototype"},
    ]
}
INDEXES = {
    "history":{"subdomains":[
        {"subdomain_id":"medieval_history","label":"História Medieval","signals":["idade média","medieval","feudalismo"],"chunks":["hist-medieval-001"]},
        {"subdomain_id":"contemporary_history","label":"História Contemporânea","signals":["revolução industrial"],"chunks":["hist-contemporary-001"]}]},
    "mathematics":{"subdomains":[
        {"subdomain_id":"algebra","label":"Álgebra","signals":["álgebra","equação"],"chunks":["math-algebra-001"]},
        {"subdomain_id":"calculus","label":"Cálculo","signals":["derivada","integral"],"chunks":["math-calculus-001"]}]},
    "portuguese":{"subdomains":[
        {"subdomain_id":"semantics","label":"Semântica","signals":["semântica","significado"],"chunks":["pt-semantics-001"]},
        {"subdomain_id":"pragmatics","label":"Pragmática","signals":["pragmática","ato de fala"],"chunks":["pt-pragmatics-001"]}]},
}

class ACLRContractsTests(unittest.TestCase):
    def test_query_contract(self):
        self.assertEqual(validate_query_request({"query_id":"q1","question":"Explique a idade média","language":"pt-BR","request_mode":"factual"})["query_id"], "q1")
    def test_invalid_query_rejected(self):
        with self.assertRaises(ContractError):
            validate_query_request({"query_id":"q1","question":"","language":"pt-BR","request_mode":"factual"})
    def test_pointer_contract(self):
        pointer={"pointer_id":"p1","schema_version":"1","target_type":"chunk","target_id":"c1","domain_ids":["history"],"concept_ids":["medieval_history"],"provenance":{},"status":"active"}
        self.assertEqual(validate_context_pointer(pointer)["pointer_id"],"p1")

class ACLRRouterTests(unittest.TestCase):
    def plan(self, question):
        return build_retrieval_plan({"query_id":"q","question":question,"language":"pt-BR","request_mode":"factual"}, MASTER, INDEXES)
    def test_single_domain_path_and_general(self):
        plan=self.plan("Explique a idade média e o feudalismo")
        self.assertTrue(any(p["domain_id"]=="history" for p in plan["paths"]))
        self.assertTrue(any(p["domain_id"] is None for p in plan["paths"]))
        targets=inspect_selected_targets(plan, INDEXES)
        self.assertIn("hist-medieval-001", [x for values in targets.values() for x in values])
    def test_cross_domain_query(self):
        plan=self.plan("Como a revolução industrial afetou a saúde e a economia?")
        domains={p["domain_id"] for p in plan["paths"]}
        self.assertIn("history",domains)
        self.assertIn(None,domains)
    def test_ambiguous_or_unknown_broadens(self):
        plan=self.plan("Explique um fenômeno ainda não catalogado")
        domains={p["domain_id"] for p in plan["paths"]}
        self.assertTrue({"history","mathematics","portuguese"}.issubset(domains))
        self.assertIn(None,domains)
    def test_requested_domain_is_hint(self):
        plan=build_retrieval_plan({"query_id":"q","question":"tema sem sinal conhecido","language":"pt-BR","request_mode":"factual","requested_domains":["history"]},MASTER,INDEXES)
        self.assertIn(None,{p["domain_id"] for p in plan["paths"]})
        self.assertIn("history",{p["domain_id"] for p in plan["paths"]})

class ACLRResolverTests(unittest.TestCase):
    def envelope(self, rid, evidence, status="success"):
        return {"query_id":"q","retriever_id":rid,"status":status,"evidence":evidence,"warnings":[]}
    def item(self, eid, content):
        return {"evidence_id":eid,"source_id":"src","document_id":"doc","chunk_id":eid,"domain_ids":["history"],"content":content,"provenance":{"source":"fixture"}}
    def test_deduplicates_and_preserves_path_status(self):
        result=resolve_evidence("q",[self.envelope("r1",[self.item("e1","Texto  igual")]),self.envelope("r2",[self.item("e2","Texto igual")],"partial")])
        self.assertEqual(result["retrieval_status"],"partial")
        self.assertEqual(len(result["evidence"]),1)
        self.assertEqual(len(result["evidence"][0]["retrieved_by"]),2)
    def test_all_empty_is_not_failure(self):
        result=resolve_evidence("q",[self.envelope("r1",[],"empty")])
        self.assertEqual(result["retrieval_status"],"complete")
        self.assertEqual(result["evidence"],[])

if __name__ == "__main__":
    unittest.main()
