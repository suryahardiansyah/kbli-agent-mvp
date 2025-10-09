# KBLI Agent MVP

**Deskripsi singkat**  
AI Agent untuk membantu petugas atau pengguna menentukan klasifikasi KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) berdasarkan deskripsi usaha / pekerjaan secara alami. Fokus awal: SE2026.

---

## Tujuan & Manfaat

- Memfasilitasi identifikasi KBLI dari teks deskriptif usaha agar lebih cepat dan akurat (proses manual sering memakan waktu).  
- Mendukung Sensus Ekonomi 2026 dengan menyediakan petugas atau komputer lokal referensi yang membantu pengklasifikasian.  
- Menyajikan hasil rekomendasi KBLI dengan “presisi” (confidence) dan metadata deskripsi KBLI.

---

## Struktur Kode & Standar KBLI 2020

- KBLI memakai **5 digit angka** untuk mengklasifikasikan kegiatan usaha.  
- Contoh kode yang valid: `01113` (Pertanian Kedelai).  
- Karena ada ~1.790 kode di KBLI 2020, agen ini akan mencari rekomendasi top-N berdasarkan teks dan memberikan “presisi” agar pengguna bisa memilih.  

---

## Contoh Input & Output (Dummy Realistis)

**Input**:  
Penjual pinang dari kebun sendiri lalu dijual di para-para pinggir jalan raya

**Output (dummy, contoh format yang diharapkan):**  
Rekomendasi KBLI:

Presisi: 42.5%
KBLI: 47221
Judul: Perdagangan eceran hasil pertanian di warung / kios
Deskripsi: Kegiatan perdagangan eceran hasil pertanian (tidak diolah) melalui gerai kecil seperti kios, warung, pedagang kaki lima, dan sejenisnya.

Presisi: 33.0%
KBLI: 01117
Judul: Pertanian biji-bijian penghasil minyak makan
Deskripsi: Kegiatan pembudidayaan tanaman biji-bijian yang menghasilkan minyak, dari pengolahan lahan, pemeliharaan, panen, dsb.

Presisi: 24.5%
KBLI: 47910
Judul: Perdagangan eceran tanaman dan bunga di luar toko
Deskripsi: Perdagangan eceran tanaman, bunga, bibit, dan tanaman pot di luar toko (misalnya pedagang kaki lima, pasar tumpah, dsb).


Catatan: nilai presisi bersifat skor internal (confidence) dari model + retrieval. Output ini hanya contoh format — kode-kode dan deskripsi di atas harus diganti dengan data nyata dari database KBLI kamu (atau referensi resmi).

---

## Fitur MVP yang Direncanakan

- Pipeline: Deskripsi teks → Retrieval (semantik / vector search) → Prompt + LLM reasoning → Output rekomendasi top-3 KBLI  
- Mode fallback: jika confidence rendah (< threshold), tampil “Maaf, saya tidak menemukan KBLI yang sesuai.”  
- Admin interface sederhana untuk memperbarui database KBLI / metadata (judul, deskripsi)  
- Export/import model atau data agar bisa diterapkan di cabang daerah  

---

## Struktur Direktori Awal yang Disarankan
/
├── README.md
├── docs/ # metadata KBLI (JSON / Markdown)
├── workflows/ # export n8n workflow JSON (tanpa credential)
├── prompts/ # template prompt (system + user)
├── src/ # kode backend / integrasi
│ ├── retriever.py
│ ├── classifier.py
│ └── api_handler.py
└── tests/ # contoh test untuk input ↔ output


---

## Kriteria “Selesai MVP”

- Agen dapat menghasilkan minimal 3 rekomendasi KBLI valid (kode 5 digit) dari input teks.  
- Metadata (judul + deskripsi) untuk KBLI ditarik dari basis data yang benar (dokumen KBLI resmi).  
- Confidence / skor ditampilkan agar pengguna tahu tingkat ketelitian.  
- Bila tidak ada rekomendasi memadai, sistem memberi pesan fallback.  
- Pipeline (retrieval + LLM) berjalan end-to-end — dari input teks ke output JSON.  
