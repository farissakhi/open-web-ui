# Open WebUI - Panduan Cepat (Windows)

> Self-hosted AI platform untuk Document Q&A dengan RAG (Retrieval Augmented Generation).

---

## 📌 QUICK START (Jalankan Setelah Restart)

### 1. Start Backend
```powershell
cd D:\PENTING\open-webui-main\backend
python start_custom.py
```

### 2. Start Frontend (terminal baru)
```powershell
cd D:\PENTING\open-webui-main
npm run dev
```

### 3. Buka Browser
```
http://localhost:5173
```

---

## 🔧 System Configuration

### Ollama Server
- **URL**: `http://10.15.42.28:11434`
- **Embedding Model**: `nomic-embed-text:latest`
- **LLM Model**: `qwen2.5:7b` (support tools)

### Ports
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8080`

---

## 📁 Struktur Project

```
D:\PENTING\open-webui-main\
├── .env                           # Configuration (RAG settings)
├── backend\
│   ├── start_custom.py          # Custom launcher script
│   └── open_webui\             # Main backend
├── src\                          # Frontend (SvelteKit)
│   └── lib\components\chat\Messages\
│       └── ResponseMessage.svelte  # Timer animation
└── test_documents\              # Dokumen testing
    ├── 01_Finance.pdf
    ├── 02_HR.pdf
    ├── 03_Marketing.pdf
    └── 04_Operations.pdf
```

---

## ⚙️ RAG Configuration (.env)

```env
OLLAMA_BASE_URL=http://10.15.42.28:11434
RAG_EMBEDDING_ENGINE=ollama
RAG_EMBEDDING_MODEL=nomic-embed-text:latest
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=150
RAG_TOP_K=10
```

### Penjelasan Parameter:

| Parameter | Value | Fungsi |
|-----------|-------|--------|
| CHUNK_SIZE | 1000 | Seberapa besar tiap potong teks |
| CHUNK_OVERLAP | 150 | Overlap antar chunks |
| TOP_K | 10 | Berapa chunks yang diambil untuk jawaban |

---

## 💬 Cara Pakai RAG

### Step 1: Upload Dokumen
```
1. Buka http://localhost:5173
2. Klik Workspace → Knowledge
3. Klik "Create Knowledge Base"
4. Upload file (PDF, DOCX, TXT)
5. Tunggu sampai selesai
```

### Step 2: Tanya Jawab
```
1. Buka halaman Chat
2. Pilih model: qwen2.5:7b
3. Klik "+" → "Attach Knowledge"
4. Pilih knowledge base yang sudah dibuat
5. Tanya!
```

### Step 3: Contoh Query yang Bagus

| ❌ Jangan | ✅ Gunakan |
|-----------|----------|
| "apa itu" | "DEFINISIKAN dan JELASKAN" |
| "siapa" | "SEBUTKAN NAMA" |
| "ringkas" | "BUAT DAFTAR LENGKAP" |
| "apa saja" | "SEBUTKAN SEMUA POIN" |

---

## 🎯 System Prompt untuk Document Q&A

Paste ini di **Chat Controls → System Prompt**:

```
=== INSTRUKSI WAJIB ===

BAHASA:
- Jawab dalam Bahasa Indonesia SE Penuh
- JANGAN campur English
- Jika ada istilah technical, translate ke Indonesia

KETEPATAN:
1. Jawab HANYA dari dokumen yang diberikan
2. Jika informasi TIDAK ADA, tulis: "Informasi ini tidak tersedia dalam dokumen"
3. JANGAN mengarang atau hallusinasi

FORMAT:
- Gunakan numbered list: "1.", "2.", "3."
- Sertakan kutipan langsung: "..."
- Jika dokumen punya 10 poin, SEBUTKAN SEMUA 10
```

---

## 🧪 Testing Documents

### Lokasi
```
D:\PENTING\open-webui-main\test_documents\
```

### Dokumen Testing (PT Nusantara Teknologi Indonesia)
1. **01_Finance.pdf** - Finance, budgeting, procurement
2. **02_HR.pdf** - HR, recruitment, leave policies
3. **03_Marketing.pdf** - Marketing, campaigns, vendors
4. **04_Operations.pdf** - Operations, facilities, SLAs

---

## 📋 90 Pertanyaan Testing

### FINANCE (Q1-20)
```
Q1: "Siapa Finance Manager di NTI?"
Q2: "Berapa budget Finance FY2026?"
Q3: "Bagaimana alur approval budget untuk Rp 60 juta?"
Q4: "Berapa batas maksimal petty cash?"
Q5: "Berapa lama invoice approval process?"
Q6: "Siapa vendor untuk IT Hardware?"
Q7: "Berapa monthly limit untuk reimbursement transportasi?"
Q8: "Bagaimana prosedur expense reimbursement?"
Q9: "Kapan budget revision harus disubmit?"
Q10: "Berapa utilized budget IT di July 2026?"
```

### HR (Q11-30)
```
Q11: "Siapa HR Manager?"
Q12: "Berapa lama probation period?"
Q13: "Jam kerja standar NTI jam berapa?"
Q14: "Berapa annual leave untuk employee permanent?"
Q15: "Kapan payroll dibayar?"
Q16: "Bagaimana proses recruitment?"
Q17: "Apa saja yang perlu di-submit saat onboarding?"
Q18: "Bagaimana approval flow untuk cuti?"
Q19: "Kapan performance review dilakukan?"
Q20: "Apa saja mandatory training?"
```

### MARKETING (Q31-50)
```
Q31: "Siapa Marketing Manager?"
Q32: "Apa primary brand color NTI?"
Q33: "Berapa total marketing budget FY2026?"
Q34: "Seberapa sering NTI posting di Instagram?"
Q35: "Approval apa untuk campaign budget Rp 50 juta?"
Q36: "Siapa vendor untuk paid digital advertising?"
Q37: "Berapa typical lead time untuk product launch?"
Q38: "Berapa allocated budget untuk Digital Advertising?"
Q39: "Kapan quarterly business review dilakukan?"
Q40: "Bagaimana coordination Marketing dengan Finance?"
```

### OPERATIONS (Q51-70)
```
Q41: "Siapa Operations Manager?"
Q42: "Berapa kapasitas office Surabaya?"
Q43: "Siapa Health & Safety Officer?"
Q44: "Apa SLA untuk access card issuance?"
Q45: "Berapa response time untuk urgent facility issue?"
Q46: "Bagaimana maintenance request process?"
Q47: "Kapan vendor performance review dilakukan?"
Q48: "Berapa reorder threshold untuk printer toner?"
Q49: "Bagaimana equipment loan process?"
Q50: "Kapan fire drill dilakukan?"
```

### CROSS-DOCUMENT (Q51-60)
```
Q51: "Siapa aja employees yang bekerja di Finance?"
Q52: "Vendor vendor mana yang overlap antar department?"
Q53: "Berapa total company budget?"
Q54: "Bagaimana coordination antar department?"
Q55: "Jika ada pertanyaan tentang employee, dokumen mana yang dibaca?"
```

---

## 🔍 Troubleshooting

### Error: "No module named 'open_webui'"
```powershell
# Pastikan virtual environment aktif
cd D:\PENTING\open-webui-main
.venv\Scripts\activate
cd backend
python start_custom.py
```

### Error: Port already in use
```powershell
# Cek port
netstat -ano | findstr :8080
netstat -ano | findstr :5173

# Kill process
taskkill /PID <process_id> /F
```

### Response time lama (~2 menit)
- Kemungkinan: Ollama server lagi load
- Coba: Model lebih kecil (qwen2.5:3b)

### Jawaban kurang akurat
- Pastikan System Prompt sudah di-set
- Pastikan Attach Knowledge sudah dipilih
- Coba query lebih spesifik

### Bahasa campur English
- Paste System Prompt yang ada di atas
- Refresh browser setelah set

---

## 📊 Performance Targets

| Metrik | Current | Target |
|--------|---------|--------|
| Response Time | ~2 menit | <30 detik |
| Accuracy | ~70% | >90% |
| Bahasa Indonesia | 70% | 100% |

---

## 🔄 Restart Setelah Update Code

Jika ada perubahan di code (frontend/backend):

### Frontend
```powershell
# Ctrl+C untuk stop
npm run dev
# Auto-reload
```

### Backend
```powershell
# Ctrl+C untuk stop
python start_custom.py
```

---

## 📝 Catatan Penting

1. **Attach Knowledge cukup sekali** per chat
2. **Model harus qwen2.5:7b** untuk RAG (support tools)
3. **Documents harus di-upload** ke Knowledge Base dulu
4. **System Prompt** harus di-set di Chat Controls

---

## 🚀 Next Steps

- [ ] Test timer animation (3 dots + timer)
- [ ] Debug response time (2 menit → <30 detik)
- [ ] Test accuracy dengan 90 pertanyaan
- [ ] Coba model lebih kecil (qwen2.5:3b)
- [ ] Setup embedding cache

---

## 📞 Links

- Open WebUI: https://github.com/open-webui/open-webui
- Ollama: https://ollama.com/
- Dokumentasi: https://docs.openwebui.com/

---

*Last Updated: 2026-09-24*
