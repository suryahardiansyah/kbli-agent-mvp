# classifier.py
# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Any
from .retriever import retrieve_kbli_topk
from .loader_bps import load_kbli_from_cache  # kita bangun lookup dari sini

# ---------- Preprocessor dialek ----------
_DIALECT_MAP = {
    r"\boj(e|a)k\b": "angkutan sepeda motor",
    r"\bojol\b": "angkutan sepeda motor",
    r"\bgrab\b": "angkutan online",
    r"\bgojek\b": "angkutan online",
    r"\bdriver\b": "pengemudi transportasi",
    r"\bpengemudi\b": "pengemudi transportasi",
    r"\bantar( |-|)jemput\b": "angkutan penumpang",
    r"\bkurir\b": "pengantar barang",
    r"\bnarik\b": "mengangkut penumpang",
    r"\border( |-|)makanan\b": "pengantaran makanan",
    r"\bwarung\b": "perdagangan eceran",
    r"\bkios\b": "perdagangan eceran",
    r"\btoko\b": "perdagangan eceran",
    r"\bkelontong\b": "perdagangan eceran",
    r"\bkuliner\b": "jasa makanan minuman",
    r"\bcloud kitchen\b": "penyediaan makanan",
    r"\bcatering\b": "penyediaan makanan",
    r"\bbikin\b": "pembuatan",
    r"\bservice\b": "jasa perbaikan",
    r"\bkebun\b": "perkebunan",
    r"\bpinang\b": "komoditas pinang",
}
class Preprocessor:
    _clean_md = re.compile(r"[*_`]+"); _spaces = re.compile(r"\s+")
    def __call__(self, text: str) -> str:
        if not text: return ""
        t = text.lower(); t = self._clean_md.sub(" ", t).strip()
        for pat, repl in _DIALECT_MAP.items(): t = re.sub(pat, repl, t)
        return self._spaces.sub(" ", t)

# ---------- kecil: domain hints ----------
_DOMAIN_HINTS: Dict[str, List[str]] = {
    "transportasi": ["angkutan","sepeda motor","penumpang","angkutan online","pengemudi transportasi","pengantar barang","jalan raya"],
    "perdagangan": ["perdagangan eceran","toko","kios","kelontong","eceran"],
    "fnb": ["penyediaan makanan","jasa makanan","minuman","kedai"],
    "pertanian": ["perkebunan","pertanian","hasil bumi","komoditas"],
    "jasa": ["jasa","layanan","perbaikan","service"],
}
def _domain_words_in(text: str)->List[str]:
    return [w for words in _DOMAIN_HINTS.values() for w in words if w in text]

_pre = Preprocessor()
_KBLI_LOOKUP: Dict[str, Dict[str, Any]] = {}
def _ensure_lookup():
    global _KBLI_LOOKUP
    if _KBLI_LOOKUP: return
    data = load_kbli_from_cache()
    _KBLI_LOOKUP = { (r.get("kode") or r.get("kbli")): {
        "kode": r.get("kode") or r.get("kbli"),
        "judul": r.get("judul",""), "deskripsi": r.get("deskripsi","")
    } for r in data if (r.get("kode") or r.get("kbli")) }

def _boost_candidates(q: str, cands: List[Dict[str,Any]])->List[Dict[str,Any]]:
    hints = set(_domain_words_in(q))
    if not hints: return cands
    out=[]
    for c in cands:
        bonus = 0.25 if any(h in f"{c.get('judul','')} {c.get('deskripsi','')}".lower() for h in hints) else 0.0
        c2=dict(c); c2["score"]=float(c2.get("score",0))+bonus; out.append(c2)
    out.sort(key=lambda x:x.get("score",0.0), reverse=True)
    return out

def classify_query(text: str)->Dict[str,Any]:
    original=text or ""; processed=_pre(original); _ensure_lookup()
    cands = retrieve_kbli_topk(processed, topk=8)     # ← konsisten dengan retriever
    cands = _boost_candidates(processed, cands)
    top1 = cands[0] if cands else {}
    code = top1.get("kbli") or top1.get("kode") if top1 else None
    if code and ("judul" not in top1 or "deskripsi" not in top1):
        row=_KBLI_LOOKUP.get(code); 
        if row: top1.setdefault("kode",row["kode"]); top1.setdefault("judul",row["judul"]); top1.setdefault("deskripsi",row["deskripsi"])
    return {"query": original, "final_choice": top1, "recommendations": cands[:5], "reasoning":"Praproses dialek + kesesuaian semantik + boost kata domain."}
