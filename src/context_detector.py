from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

CONTEXTS = {
    "pertanian": ["kebun", "menanam", "hasil panen", "perkebunan", "pertanian"],
    "perdagangan": ["menjual", "toko", "dagang", "eceran", "penjualan", "pasar"],
    "industri": ["pabrik", "produksi", "pengolahan", "industri", "manufaktur"],
    "jasa": ["servis", "layanan", "pengujian", "pelatihan", "perawatan"],
    "transportasi": ["angkutan", "pengiriman", "logistik", "ekspedisi", "kurir"]
}

# Pre-encode context examples
context_texts = [w for c in CONTEXTS.values() for w in c]
context_emb = model.encode(context_texts, convert_to_tensor=True)

def detect_context(query: str):
    query_emb = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, context_emb)[0]

    idx_best = int(cos_scores.argmax())
    all_words = [w for c in CONTEXTS.values() for w in c]

    # Find which context this word belongs to
    for ctx, words in CONTEXTS.items():
        if all_words[idx_best] in words:
            return ctx
    return None
