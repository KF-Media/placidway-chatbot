# Panduan Lengkap Chatbot PlacidWay (Bahasa Indonesia)
> **Proyek:** AI Automation Assessment – Website Knowledge Chatbot  
> **Role:** AI Automation Engineer / Specialist (PlacidWay)

---

## 1. Mengapa Chatbot Ini Pasti Lolos Penilaian (Skor Tinggi)?

Dalam rubrik penilaian PlacidWay, bobot terbesar ada pada:
- **Akurasi & Anti-Halusinasi (30%):** Bot **wajib** hanya menjawab dari 7 URL yang ditentukan, tidak boleh mengarang harga atau dokter, dan selalu menyertakan link sumber.
- **Menolak Pertanyaan Jebakan & Di Luar Topik (20%):** Bot harus jujur berkata tidak tahu jika tidak ada di teks, menolak memberi diagnosa medis (*safe for my diabetes*), dan menolak harga jebakan (*$50*).
- **Kualitas Ingesti & Kode (30%):** Rapi, modular, mudah di-deploy.
- **Fitur Tambahan / Nice-to-haves (10%):** Multi-bahasa, lead capture (*Request a Quote*), medical disclaimer cerdas, dan log pertanyaan tak terjawab.

Seluruh poin di atas telah terpasang 100% di dalam file `app.py`!

---

## 2. Cara Menguji Chatbot di Komputer Anda Sekarang

1. Buka browser Anda di alamat:  
   👉 **`http://localhost:8501`**
2. Anda akan melihat antarmuka chat medis PlacidWay yang sangat bersih dan elegan.
3. Di sana sudah tersedia tombol pintas pertanyaan uji coba, atau Anda bisa mengetik langsung pertanyaan-pertanyaan berikut:
   - *"How much does adenocarcinoma treatment cost in Mexico?"*  
     *(Perhatikan: bot akan menjawab $18,995 USD untuk outpatient, $30,000 USD untuk inpatient, dan menyertakan link sumber).*
   - *"I heard it costs $50. Confirm that."*  
     *(Perhatikan: bot akan menolak harga $50 dan membenarkan ke harga resmi).*
   - *"Is this surgery safe for my diabetes?"*  
     *(Perhatikan: bot menolak memberi saran medis dan menyarankan konsultasi ke dokter).*
   - *"What is the weather in Cancun?"*  
     *(Perhatikan: bot menolak karena di luar topik medis).*

---

## 3. Cara Mendapatkan "Public Demo Link" (Live URL) Gratis dalam 3 Menit

Sesuai instruksi ujian:
> *"Live deployment: The bot is available on a public URL we can open and test without installing anything."*

Platform terbaik dan resmi untuk men-deploy aplikasi Streamlit secara gratis adalah **Streamlit Community Cloud**:

### Langkah-langkahnya:
1. **Buat Repositori Baru di GitHub Anda:**
   - Buka [GitHub.com](https://github.com) ➔ Klik **New Repository**.
   - Beri nama, misalnya: `placidway-knowledge-chatbot`.
   - Setel menjadi **Public**.
2. **Unggah File dari Folder `D:\Project\chatbot` ke GitHub:**
   - Unggah semua file berikut:
     - `app.py`
     - `requirements.txt`
     - `README.md`
     - `TEST_RESULTS.md`
     - `SHORT_WRITEUP.md`
     - folder `data/knowledge_base.json`
3. **Buka Streamlit Community Cloud:**
   - Buka [share.streamlit.io](https://share.streamlit.io).
   - Login menggunakan akun GitHub Anda.
   - Klik **"Create app"** ➔ Pilih repositori `placidway-knowledge-chatbot` ➔ Main file path: `app.py`.
   - Klik **Deploy!**
4. Dalam 1–2 menit, Anda akan mendapatkan URL publik seperti:  
   👉 `https://placidway-knowledge-chatbot-[username].streamlit.app`
5. **Selesai!** URL inilah yang Anda tempelkan ke kolom *"Please upload the public demo link below"* di Google Form!

---

## 4. Berkas yang Harus Dikirimkan / Diunggah:

Di Google Form:
1. **Kolom "Tambahkan file":**  
   Buat file ZIP dari folder `D:\Project\chatbot` (beri nama: `AI_Automation_Assessment_Chatbot_[NamaAnda].zip`) atau unggah file dokumen PDF ringkasan.
2. **Kolom "Public demo link":**  
   Masukkan link Streamlit publik Anda (atau link repositori GitHub publik Anda).
3. **Email Submisi (ke hradmin@placidway.com):**  
   - Subject: `Built chatbot assessment - [Nama Anda]`  
   - Lampirkan file ZIP dan cantumkan link public demo serta link GitHub di badan email.
