# retriever.py
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from src.loader_bps import load_kbli_from_cache

model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model = SentenceTransformer(model_name)

KBLI_DATA = load_kbli_from_cache()
EMBED_CACHE = "data/kbli_embeddings_bps.npy"

if os.path.exists(EMBED_CACHE):
    EMBEDDINGS = np.load(EMBED_CACHE)
else:
    texts = [f"{row['judul']} {row['deskripsi']}" for row in KBLI_DATA]
    EMBEDDINGS = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    np.save(EMBED_CACHE, EMBEDDINGS)

def retrieve_kbli_topk(query: str, topk: int = 8):
    """
    Return list[dict] sorted desc by score:
      {"kbli": <kode5>, "kode": <kode5>, "judul": ..., "deskripsi": ..., "score": float}
    """
    q_emb = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(q_emb, EMBEDDINGS)[0].cpu().numpy()

    idx = np.argsort(-scores)[:topk]
    out = []
    for i in idx:
        row = KBLI_DATA[i]
        out.append({
            "kbli": row.get("kode") or row.get("kbli"),
            "kode": row.get("kode") or row.get("kbli"),
            "judul": row.get("judul", ""),
            "deskripsi": row.get("deskripsi", ""),
            "score": float(scores[i]),
        })
    return out
