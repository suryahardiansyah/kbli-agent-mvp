import os
import json
import torch
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
print(f"[INFO] Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

DATA_PATH = os.path.join("docs", "kbli_2020.json")
CACHE_PATH = "kbli_embeddings.pt"

def load_kbli_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File {DATA_PATH} tidak ditemukan. Pastikan sudah ada.")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[INFO] Loaded {len(data)} entri KBLI.")
    return data

KBLI_DATA = load_kbli_data()

def get_embeddings():
    if os.path.exists(CACHE_PATH):
        print("[INFO] Loading cached embeddings...")
        return torch.load(CACHE_PATH)
    print("[INFO] Encoding KBLI data (sekali saja, agak lama)...")
    embeddings = model.encode([x["deskripsi"] for x in KBLI_DATA], convert_to_tensor=True)
    torch.save(embeddings, CACHE_PATH)
    return embeddings

KBLI_EMB = get_embeddings()

def retrieve_kbli(query, top_k=3):
    print(f"[DEBUG] Query masuk: {query}")
    if not query.strip():
        return []
    query_emb = model.encode(query, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(query_emb, KBLI_EMB)[0]
    top_results = cos_scores.topk(k=min(top_k, len(KBLI_DATA)))
    results = [(float(cos_scores[i]), KBLI_DATA[i]) for i in top_results[1]]
    print(f"[DEBUG] Hasil retrieve: {results}")
    return results
