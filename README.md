# KBLI Agent MVP

## Deskripsi Singkat / Short Description
AI Agent untuk membantu petugas atau pengguna menentukan klasifikasi **KBLI (Klasifikasi Baku Lapangan Usaha Indonesia)** berdasarkan deskripsi usaha atau pekerjaan secara alami.  
An AI Agent designed to help field officers or users determine the appropriate **KBLI (Indonesian Standard Industrial Classification)** code based on natural business or job descriptions.  
**Fokus awal / Initial focus:** SE2026.

---

## Tujuan dan Manfaat / Goals and Benefits

### Bahasa Indonesia
- Memfasilitasi identifikasi KBLI dari teks deskriptif usaha agar lebih cepat dan akurat karena proses manual sering memakan waktu.  
- Mendukung **Sensus Ekonomi 2026 (SE2026)** dengan menyediakan referensi lokal berbasis AI untuk membantu pengklasifikasian usaha.  
- Menyajikan hasil rekomendasi KBLI dengan nilai presisi (confidence) dan metadata deskripsi resmi.

### English
- Facilitate faster and more accurate KBLI identification from natural-language business descriptions since manual processing is often time-consuming.  
- Support **Economic Census 2026 (SE2026)** by providing a local AI-based reference to assist in business classification.  
- Provide KBLI recommendations with confidence scores and official KBLI metadata.

---

## Struktur Kode dan Standar KBLI 2020 / Code Structure and KBLI 2020 Standard

### Bahasa Indonesia
- KBLI menggunakan **5 digit angka** untuk mengklasifikasikan kegiatan usaha.  
- Contoh kode valid: `01113` (Pertanian Kedelai).  
- Karena ada sekitar **1.790 kode** dalam KBLI 2020, agen ini akan mencari **top-N rekomendasi** berdasarkan teks dan memberikan nilai presisi.

### English
- KBLI uses **5-digit numeric codes** to classify business activities.  
- Example of a valid code: `01113` (Soybean Farming).  
- Since there are about **1,790 codes** in KBLI 2020, the agent retrieves **top-N recommendations** based on text similarity and provides a precision score.

---

## Contoh Input dan Output / Example Input and Output

### Input
**ID:** Penjual pinang dari kebun sendiri lalu dijual di para-para pinggir jalan raya  
**EN:** Seller of areca nuts from own garden, sold at roadside stalls

### Output (dummy, contoh format yang diharapkan / expected format)

**Presisi:** 42.5%  
**KBLI:** 47221  
**Judul:** Perdagangan eceran hasil pertanian di warung atau kios  
**Deskripsi:** Kegiatan perdagangan eceran hasil pertanian (tidak diolah) melalui gerai kecil seperti kios, warung, pedagang kaki lima, dan sejenisnya.

**Presisi:** 33.0%  
**KBLI:** 01117  
**Judul:** Pertanian biji-bijian penghasil minyak makan  
**Deskripsi:** Kegiatan pembudidayaan tanaman biji-bijian yang menghasilkan minyak, dari pengolahan lahan, pemeliharaan, panen, dan seterusnya.

**Presisi:** 24.5%  
**KBLI:** 47910  
**Judul:** Perdagangan eceran tanaman dan bunga di luar toko  
**Deskripsi:** Perdagangan eceran tanaman, bunga, bibit, dan tanaman pot di luar toko seperti pedagang kaki lima atau pasar tumpah.

### Catatan / Note
Nilai presisi adalah skor internal dari model dan retrieval. Contoh di atas hanya format.  
Kode dan deskripsi harus disesuaikan dengan **database KBLI resmi**.  
The precision value is an internal score from the model and retrieval.  
The example above is a format only — replace codes and descriptions with official KBLI data.

---

## Fitur MVP yang Direncanakan / Planned MVP Features

### Bahasa Indonesia
- **Alur:** Deskripsi teks → Retrieval (semantic atau vector search) → Prompt + LLM reasoning → Rekomendasi KBLI top-3  
- **Mode fallback:** Jika confidence di bawah ambang batas, tampilkan pesan *"Maaf, saya tidak menemukan KBLI yang sesuai."*  
- **Antarmuka admin sederhana** untuk memperbarui database KBLI (judul dan deskripsi).  
- **Dukungan ekspor/impor** agar dapat diterapkan di kantor daerah.

### English
- **Pipeline:** Text description → Retrieval (semantic or vector search) → Prompt + LLM reasoning → Top-3 KBLI recommendations  
- **Fallback mode:** If confidence is below threshold, display *"Sorry, I could not find a suitable KBLI."*  
- **Simple admin interface** for updating the KBLI database (title and description).  
- **Export/import support** for regional deployment.

---

## Struktur Direktori Awal / Suggested Directory Structure
/
├── README.md
├── docs/ # metadata KBLI (JSON atau Markdown)
├── workflows/ # exported n8n workflows (no credentials)
├── prompts/ # system dan user prompt templates
├── src/ # backend atau integration code
│ ├── retriever.py
│ ├── classifier.py
│ └── api_handler.py
└── tests/ # example tests for input and output

---

## Kriteria Selesai MVP / MVP Completion Criteria

### Bahasa Indonesia
- Agen mampu menghasilkan minimal **3 rekomendasi KBLI valid (5 digit)** dari input teks.  
- Metadata (judul dan deskripsi) diambil dari **database resmi KBLI**.  
- Confidence score ditampilkan agar pengguna tahu tingkat akurasi.  
- Bila tidak ada hasil relevan, tampilkan pesan fallback.  
- Pipeline retrieval dan LLM berjalan **end-to-end** dari input teks ke output JSON.

### English
- The agent must produce at least **3 valid 5-digit KBLI recommendations** from text input.  
- Metadata (title and description) must come from the **official KBLI dataset**.  
- Confidence score must be displayed to indicate reliability.  
- If no relevant result is found, display a fallback message.  
- Retrieval and LLM pipeline must work **end-to-end** from text input to JSON output.

