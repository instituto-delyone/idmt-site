import unittest
import asyncio
import json
from pathlib import Path

from aclr_router import build_retrieval_plan, inspect_selected_targets
from aclr_contracts import (ContractError, validate_query_request, validate_context_pointer, validate_library_manifest, validate_retrieval_plan, validate_evidence_envelope)
from aclr_resolver import resolve_evidence
from aclr_adapters import library_results_to_envelope, r2_results_to_envelope
from aclr_orchestrator import execute_retrieval_plan

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
    def test_manifest_contract(self):
        manifest={"manifest_version":"1","library_id":"test","created_at":"2026-11-01T00:00:00Z","domains":[],"general_index":{"index_key":"library/general/index/","version":"1"}}
        self.assertEqual(validate_library_manifest(manifest)["library_id"],"test")
    def test_all_json_schemas_parse(self):
        schema_dir=Path(__file__).parents[1]/"aclr"/"schemas"
        for path in schema_dir.glob("*.schema.json"):
            with self.subTest(schema=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")),dict)

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

class ACLROrchestratorTests(unittest.TestCase):
    def test_one_failed_path_preserves_successful_paths(self):
        plan=build_retrieval_plan({"query_id":"q","question":"idade média","language":"pt-BR","request_mode":"factual"},MASTER,INDEXES)
        async def retrieve(path):
            if path["domain_id"] is None:
                raise RuntimeError("simulated general-index failure")
            return {"query_id":"q","retriever_id":path["path_id"],"status":"success","evidence":[],"warnings":[]}
        result=asyncio.run(execute_retrieval_plan(plan,retrieve,max_concurrency=2))
        self.assertEqual(result["retrieval_status"],"partial")
        self.assertTrue(any(x["status"]=="error" for x in result["path_results"]))
        self.assertTrue(any(x["status"]=="success" for x in result["path_results"]))

class ACLRAdapterTests(unittest.TestCase):
    def test_library_adapter_preserves_source_and_score_semantics(self):
        envelope=library_results_to_envelope("q",[{"text":"Passagem de teste","chunk_id":"chunk-1","source_key":"book-a","score":0.82}])
        self.assertEqual(envelope["evidence"][0]["chunk_id"],"chunk-1")
        self.assertEqual(envelope["evidence"][0]["source_id"],"book-a")
        self.assertIsNone(envelope["evidence"][0]["confidence"])
        self.assertEqual(envelope["evidence"][0]["relevance_score"],0.82)
    def test_r2_adapter_keeps_checksum_provenance(self):
        envelope=r2_results_to_envelope("q",[{"text":"Texto","chunk_id":"r2-chunk","document_id":"doc-1","checksum":"abc","retrieval_method":"lexical"}])
        self.assertEqual(envelope["evidence"][0]["provenance"]["checksum"],"abc")
        self.assertEqual(envelope["status"],"success")

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
    def test_claim_conflict_is_preserved(self):
        first=self.item("e1","A proposição foi confirmada.")
        second=self.item("e2","A proposição foi refutada.")
        first["provenance"]["claim_id"]="claim-1"
        second["provenance"]["claim_id"]="claim-1"
        result=resolve_evidence("q",[self.envelope("r1",[first]),self.envelope("r2",[second])])
        self.assertEqual(len(result["evidence"]),2)
        self.assertEqual(len(result["conflicts"]),1)
        self.assertEqual(result["conflicts"][0]["resolution"],"unresolved_preserve_all")

if __name__ == "__main__":
    unittest.main()
