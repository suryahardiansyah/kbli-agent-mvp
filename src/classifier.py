from retriever import retrieve_kbli
from context_detector import detect_context
from hierarchy import format_hierarchy

def format_for_chat(result): 
    """ Format hasil klasifikasi agar tampil informatif seperti chatbot WhatsApp. """ 
    if not result or not result.get("recommendations"): 
        return "Tidak ditemukan hasil yang cocok untuk deskripsi tersebut." 
    tips = ( "*Tips Pencarian*\n" "Gunakan tanda petik dua (\") untuk mencari kata gabung.\n" 
            "Contoh: \"kaca mata\" → hasil hanya yang memuat frasa itu.\n" ) 
    header = f"\nMenemukan {len(result['recommendations'])} hasil relevan.\n" 
    recs = [] 
    for i, r in enumerate(result["recommendations"], 1): recs.append( f"{i}. KBLI {r['kbli']} - {r['judul']}\n" f"{r['deskripsi']}\n" ) 
    summary = ( f"\n*Final Choice:* KBLI {result['final_choice']}\n" f"{result['reasoning']}" )
    recs = format_hierarchy(result["recommendations"])
    return f"{tips}\n{header}\n{recs}\n\n{summary}"

def mock_llm_reasoning(query, retrieved):
    """
    Reasoning berbasis konteks semantik (unsupervised).
    """
    if not retrieved:
        return {
            "query": query,
            "recommendations": [],
            "final_choice": None,
            "reasoning": "Tidak ditemukan hasil yang relevan."
        }

    context = detect_context(query) or "umum"
    best = max(retrieved, key=lambda x: x[0])
    best_kbli = best[1]["kbli"]

    reason = f"karena konteks terdekat adalah '{context}' dan hasil KBLI {best_kbli} paling relevan."

    recommendations = [
        {
            "presisi": round(score * 100, 2),
            "kbli": entry["kbli"],
            "judul": entry["judul"],
            "deskripsi": entry["deskripsi"]
        }
        for score, entry in retrieved
    ]

    return {
        "query": query,
        "recommendations": recommendations,
        "final_choice": best_kbli,
        "reasoning": f"Saya memilih KBLI {best_kbli} ('{best[1]['judul']}') {reason}"
    }

def classify_query(query):
    retrieved = retrieve_kbli(query)
    return mock_llm_reasoning(query, retrieved)
