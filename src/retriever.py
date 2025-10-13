import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from loader_bps import load_kbli_from_cache

model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
print(f"[INFO] Loading model: {model_name}")
model = SentenceTransformer(model_name)

# === LOAD DATA FROM BPS ===
KBLI_DATA = load_kbli_from_cache()
print(f"[INFO] Loaded {len(KBLI_DATA)} KBLI entries from BPS WebAPI.")

EMBED_CACHE = "data/kbli_embeddings_bps.npy"

if os.path.exists(EMBED_CACHE):
    print("[INFO] Loading cached embeddings...")
    EMBEDDINGS = np.load(EMBED_CACHE)
else:
    print("[INFO] Creating new embeddings cache...")
    texts = [f"{row['judul']} {row['deskripsi']}" for row in KBLI_DATA]
    EMBEDDINGS = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    np.save(EMBED_CACHE, EMBEDDINGS)
    print("[INFO] Embeddings cached from BPS data.")

def retrieve_kbli(query, top_k=5):
    query_emb = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_emb, EMBEDDINGS)[0]

    results = []
    for i, score in enumerate(cosine_scores):
        entry = KBLI_DATA[i]
        results.append((float(score), entry))

    return sorted(results, key=lambda x: x[0], reverse=True)[:top_k]

'''
If someday you want to refresh the cache (for example, when BPS announces new KBLI),
you can just run:

python -c "from bps_loader import load_kbli_from_cache; load_kbli_from_cache(force_refresh=True)"

'''