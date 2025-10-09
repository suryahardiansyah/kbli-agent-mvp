import gradio as gr
from classifier import classify_query

def classify_interface(query):
    try:
        if not query or not query.strip():
            return "Silakan masukkan deskripsi usaha terlebih dahulu."

        result = classify_query(query)
        if not result or not result.get("recommendations"):
            return "Tidak ditemukan hasil yang cocok untuk deskripsi tersebut."
        
        final = result["final_choice"]
        reasoning = result["reasoning"]
        recs = "\n".join([
            f"- {r['kbli']} ({r['presisi']}%) - {r['judul']}"
            for r in result["recommendations"]
        ])
        
        return f"**Final KBLI:** {final}\n\n**Rekomendasi:**\n{recs}\n\n**Penjelasan:** {reasoning}"
    
    except Exception as e:
        import traceback
        print("[ERROR]", e)
        print(traceback.format_exc())
        return f"Terjadi error di server:\n\n{str(e)}"


# === GRADIO APP ===
demo = gr.Interface(
    fn=classify_interface,
    inputs=gr.Textbox(label="Deskripsi Usaha", placeholder="Contoh: penjual pinang dari kebun sendiri dijual di para-para pinggir jalan"),
    outputs="markdown",
    title="KBLI Agent MVP (Chat Demo)",
    description="Uji coba AI Agent KBLI untuk deskripsi usaha. Contoh: 'penjual pinang dari kebun sendiri dijual di para-para pinggir jalan'."
)

if __name__ == "__main__":
    demo.launch()
