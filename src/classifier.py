from retriever import retrieve_kbli

def simple_reasoning(query, retrieved):
    """
    Versi reasoning ringan tanpa LLM.
    """
    if not retrieved:
        return {
            "query": query,
            "recommendations": [],
            "final_choice": None,
            "reasoning": "Tidak ada hasil yang ditemukan."
        }

    best = max(retrieved, key=lambda x: x[0])
    explanation = (
        f"Saya memilih KBLI {best[1]['kbli']} ('{best[1]['judul']}') "
        f"karena deskripsinya paling relevan dengan teks '{query}'."
    )
    return {
        "query": query,
        "recommendations": [
            {
                "presisi": round(score * 100, 2),
                "kbli": entry["kbli"],
                "judul": entry["judul"],
                "deskripsi": entry["deskripsi"],
            }
            for score, entry in retrieved
        ],
        "final_choice": best[1]["kbli"],
        "reasoning": explanation
    }

def classify_query(query):
    retrieved = retrieve_kbli(query)
    return simple_reasoning(query, retrieved)

if __name__ == "__main__":
    query = "penjual pinang dari kebun sendiri dijual di para para pinggir jalan"
    result = classify_query(query)
    print("\n=== HASIL REKOMENDASI ===")
    for rec in result["recommendations"]:
        print(f"{rec['kbli']} ({rec['presisi']}%) - {rec['judul']}")
    print("\nFinal choice:", result["final_choice"])
    print("Reasoning:", result["reasoning"])
