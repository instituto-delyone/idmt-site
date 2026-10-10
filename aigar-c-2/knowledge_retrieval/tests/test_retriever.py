from __future__ import annotations

import json
from AIGAR_LIBRARY.retriever import LibraryRetriever


def test_search_load_and_reconstruct(tmp_path):
    root = tmp_path / "library"
    (root / "indexes").mkdir(parents=True)
    (root / "cache" / "demo").mkdir(parents=True)

    ids = ["DEMO-A", "DEMO-B"]
    for cid, text in zip(ids, [
        "história da humanidade linguagem cooperação",
        "história da matemática números e linguagem"
    ]):
        (root / "cache" / "demo" / f"{cid}.txt").write_text(text, encoding="utf-8")

    index = {"chunks":[
        {"id":"DEMO-A","source_key":"demo","source":"demo.txt","sequence":1},
        {"id":"DEMO-B","source_key":"demo","source":"demo.txt","sequence":2}
    ]}
    (root / "indexes" / "demo.index.json").write_text(json.dumps(index), encoding="utf-8")

    retriever = LibraryRetriever(root)
    hits = retriever.search("história humanidade")
    assert hits[0]["id"] == "DEMO-A"
    assert "cooperação" in retriever.load("DEMO-A")["text"]
    assert [x["id"] for x in retriever.reconstruct(ids)] == ids
