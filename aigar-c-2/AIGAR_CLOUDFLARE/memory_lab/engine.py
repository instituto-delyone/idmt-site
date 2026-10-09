"""AIGAR Memory Lab: isolated three-layer repository-backed retrieval."""
from __future__ import annotations
import json, re, time
from urllib.parse import quote
MEMORY_LAYERS = {"imediata":"memoria_imediata","curto_prazo":"memoria_curto_prazo","longo_prazo":"memoria_longo_prazo"}
DEFAULT_CONFIG = {"enabled":True,"repository":"instituto-delyone/idmt-site","ref":"main","root":"aigar-c-2/AIGAR_CLOUDFLARE/memory_lab","refresh_seconds":60,"short_term_top_k":3,"long_term_top_k":4,"max_document_chars":120000}
def _terms(text): return set(re.findall(r"[a-zA-ZÀ-ÿ0-9_+-]{2,}", (text or "").lower()))
def _score(query, content, name=""): return len(_terms(query) & _terms((name or "")+" "+(content or "")))
class MemoryLab:
    def __init__(self, fetcher, config=None):
        self.fetcher=fetcher; self.config={**DEFAULT_CONFIG,**(config or {})}
        self.documents={k:[] for k in MEMORY_LAYERS}; self._last_scan=0
        self.status={"enabled":self.config["enabled"],"ready":False,"mode":"not_initialized","layers":{},"last_scan":None,"error":None}
    async def _request(self,url,json_response=False):
        response=await self.fetcher(url,{"headers":{"User-Agent":"AIGAR-Memory-Lab/1.0","Accept":"application/vnd.github+json"}})
        if not getattr(response,"ok",False): raise RuntimeError("HTTP "+str(getattr(response,"status","?"))+" fetching "+url)
        return await response.json() if json_response else await response.text()
    async def initialize(self,force=False):
        if not self.config.get("enabled"):
            self.status.update({"enabled":False,"ready":False,"mode":"disabled"}); return self.get_status()
        now=time.time()
        if not force and self.status.get("ready") and now-self._last_scan<int(self.config["refresh_seconds"]): return self.get_status()
        repo,ref=self.config["repository"],quote(str(self.config["ref"]),safe="")
        try:
            config_path=self.config["root"].strip("/") + "/config.json"
            encoded_config="/".join(quote(part,safe="") for part in config_path.split("/"))
            try:
                remote_config=await self._request(f"https://raw.githubusercontent.com/{repo}/{ref}/{encoded_config}")
                parsed_config=json.loads(remote_config)
                allowed={"enabled","repository","ref","root","refresh_seconds","short_term_top_k","long_term_top_k","max_document_chars"}
                self.config.update({k:v for k,v in parsed_config.items() if k in allowed})
                repo,ref=self.config["repository"],quote(str(self.config["ref"]),safe="")
            except Exception:
                # A broken config must not take down AIGAR; continue with safe defaults.
                pass
            root=self.config["root"].strip("/")
            tree=await self._request(f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1",True)
            if tree.get("truncated"): raise RuntimeError("GitHub tree truncated; cannot guarantee complete discovery")
            paths=[x.get("path","") for x in tree.get("tree",[]) if x.get("type")=="blob"]
            docs={k:[] for k in MEMORY_LAYERS}; stats={k:{"files_found":0,"files_loaded":0,"errors":[]} for k in MEMORY_LAYERS}
            for layer,folder in MEMORY_LAYERS.items():
                candidates=[p for p in paths if p.startswith(root+"/"+folder+"/") and p.lower().endswith(".txt")]
                stats[layer]["files_found"]=len(candidates)
                for path in candidates:
                    try:
                        encoded="/".join(quote(part,safe="") for part in path.split("/"))
                        content=await self._request(f"https://raw.githubusercontent.com/{repo}/{ref}/{encoded}")
                        content=content[:int(self.config["max_document_chars"])]
                        if not content.strip(): raise RuntimeError("empty document")
                        docs[layer].append({"path":path,"name":path.rsplit("/",1)[-1],"content":content,"chars":len(content)})
                        stats[layer]["files_loaded"]+=1
                    except Exception as exc: stats[layer]["errors"].append({"path":path,"error":str(exc)[:250]})
            self.documents=docs; im=stats["imediata"]; ready=im["files_found"]==im["files_loaded"]
            self.status={"enabled":True,"ready":ready,"mode":"ready" if ready else "partial","layers":stats,"last_scan":int(now),"error":None if ready else "One or more immediate-memory TXT files failed to load."}
            self._last_scan=now
        except Exception as exc: self.status.update({"ready":False,"mode":"error","error":str(exc)[:500]})
        return self.get_status()
    def retrieve(self,query,layer,limit=None):
        ranked=[]
        for doc in self.documents.get(layer,[]):
            score=_score(query,doc["content"],doc["name"])
            if score: ranked.append((score,doc))
        ranked.sort(key=lambda x:x[0],reverse=True)
        default=self.config["short_term_top_k"] if layer=="curto_prazo" else self.config["long_term_top_k"]
        return [{"layer":layer,"path":d["path"],"name":d["name"],"score":s,"content":d["content"]} for s,d in ranked[:int(limit or default)]]
    async def retrieve_with_fallback(self,query):
        status=await self.initialize()
        if not self.config.get("enabled"): return {"ok":False,"status":status,"selected_layer":[],"documents":[]}
        immediate=self.retrieve(query,"imediata",3); short=self.retrieve(query,"curto_prazo"); selected=immediate+short
        layers=["imediata","curto_prazo"] if selected else []
        if not selected:
            selected=self.retrieve(query,"longo_prazo"); layers=["longo_prazo"] if selected else []
        return {"ok":bool(selected),"status":status,"selected_layer":layers,"documents":selected}
    def get_status(self):
        return {**self.status,"document_counts":{k:len(v) for k,v in self.documents.items()},"config":{k:v for k,v in self.config.items() if k not in {"token","secret","api_key"}}}
