# Open WebUI RAG Setup - Local Development

## Progress Update: 28 September 2026

### Yang Sudah Berhasil

1. **Open WebUI Backend Running**
   - URL: http://localhost:5173
   - Backend folder: `D:\PENTING\open-webui-main\backend`
   - Start command: `py -3.11 -m uvicorn main:app --host 0.0.0.0 --port 5173 --reload`

2. **Ollama Server**
   - URL: http://10.15.42.28:11434
   - Models available:
     - `nomic-embed-text:latest` (embedding model)
     - `qwen2.5:3b` (chat model)
     - `llama3.2:latest`
     - `mistral:latest`

3. **Login Credentials**
   - Email: farissakhii@gmail.com
   - Password: admin123

4. **Knowledge Base: DokumenNTI** - BERHASIL DIBUAT
   - 4 files uploaded & indexed:
     - 01_Finance.pdf (62 chunks)
     - 02_HR.pdf (74 chunks)
     - 03_Marketing.pdf (48 chunks)
     - 04_Operations.pdf (58 chunks)
   - Total: 242 embedding chunks di ChromaDB
   - KB ID: cb43f792-1f94-481f-bed7-4718d17339a8

5. **Database**
   - SQLite: `backend\data\webui.db`
   - ChromaDB: `backend\data\vector_db\chroma.sqlite3` (3.7 MB)

### Yang Belum Berhasil / Pending

1. **RAG Query Test** - BELUM BERHASIL
   - Problem: Default model "nomic-embed-text:latest" adalah embedding model, bukan chat model
   - Perlu: Pilih chat model (qwen2.5:3b, llama3.2, mistral) sebelum chat
   - Script ready: `test_rag_query_v2.py` tapi belum dijalankan

2. **Playwright Automation Scripts**
   - Versi working: `test_rag_v8.py` - untuk KB creation & upload
   - Versi pending: `test_rag_query_v2.py` - untuk query test

### File Scripts Penting

```
D:\PENTING\open-webui-main\
├── test_rag_v8.py              # Working - KB creation & file upload
├── test_rag_query_v2.py        # Pending - RAG query test
├── check_db3.py                # Cek database state
├── check_kb_embeddings.py      # Cek embeddings di ChromaDB
└── test_results\               # Screenshot & report results
    ├── report.json
    ├── 04_kb_created.png
    ├── 06_after_upload.png
    └── query_results.json (belum ada)
```

### Langkah Selanjutnya (Lanjutkan Besok)

1. Jalankan `test_rag_query_v2.py` untuk test RAG query
2. Pastikan pilih chat model (bukan embedding model) sebelum chat
3. Test query seperti:
   - "Siapa Finance Manager di NTI?"
   - "Apa produk yang dijual NTI?"
   - "Siapa CEO NTI?"
4. Ukur response time & akurasi jawaban

### Konfigurasi .env

```
RAG_EMBEDDING_ENGINE=ollama
RAG_TOP_K=3
ENABLE_PLUGINS=false
OLLAMA_BASE_URL=http://10.15.42.28:11434
```

---

## Original README (Open WebUI Project)

[Standard Open WebUI README continues below...]
