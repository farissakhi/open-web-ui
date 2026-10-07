# Open WebUI - Alur Pipeline & Dokumentasi Kode

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Pipeline Alur Request-Response](#2-pipeline-alur-request-response)
3. [RAG Pipeline (Upload Dokumen → Tanya Jawab)](#3-rag-pipeline-upload-dokumen--tanya-jawab)
4. [Chat Pipeline](#4-chat-pipeline)
5. [Ollama Integration](#5-ollama-integration)
6. [Database & Model](#6-database--model)
7. [Key Files Reference](#7-key-files-reference)
8. [Setup Guide](#8-setup-guide)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                  (SvelteKit Frontend - Port 5173)               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP / WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8080)                   │
│                   backend/open_webui/main.py                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              31 FastAPI Routers (/api/v1/*)              │    │
│  │                                                           │    │
│  │  /auths    → Login, OAuth, LDAP, API Key                  │    │
│  │  /users    → User profile, permissions                    │    │
│  │  /chats    → Chat CRUD, history, sharing                  │    │
│  │  /models   → Model registry, configs                      │    │
│  │  /retrieval → RAG: upload, chunk, embed, query            │    │
│  │  /ollama    → Ollama proxy + OpenAI-compatible            │    │
│  │  /openai    → OpenAI API proxy + Azure + Anthropic        │    │
│  │  /knowledge → Knowledge base CRUD                         │    │
│  │  /functions → Pipeline/filter function management         │    │
│  │  /audio     → Whisper STT, TTS                           │    │
│  │  /images    → Image generation                            │    │
│  │  /admin     → Admin operations                            │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │
│  │  Socket.IO     │  │  SQLAlchemy    │  │  Vector DB     │      │
│  │  (/ws)         │  │  ORM           │  │  (ChromaDB)    │      │
│  │  - Streaming   │  │  - SQLite      │  │  - Embeddings  │      │
│  │  - Yjs/CRDT    │  │  - Postgres    │  │  - Top-K       │      │
│  └────────────────┘  └────────────────┘  └────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Ollama      │  │ Vector DB    │  │   Redis      │
│   (Local LLM) │  │ (ChromaDB)  │  │  (Optional)  │
│               │  │              │  │              │
│ /api/chat    │  │ Chroma       │  │ Session pool │
│ /api/embed   │  │ pgvector    │  │ Pub/sub     │
│ /api/generate│  │ Qdrant      │  │              │
└───────────────┘  │ Milvus      │  └───────────────┘
                   │ Weaviate    │
                   │ Pinecone    │
                   │ ...         │
                   └───────────────┘
```

---

## 2. Pipeline Alur Request-Response

### 2.1 User Request → LLM → Response

```
[1] User ketik pesan di Chat UI (SvelteKit)
         │
         ▼
[2] Frontend kirim POST /api/v1/chat/completions
         │
         ▼
[3] Auth Middleware (JWT cookie / Bearer token)
         │
         ▼
[4] Chat Router → Cek model, permission
         │
         ▼
[5] Pipeline/Filter System
         │  ├── Inlet Filter (transform input)
         │  └── Outlet Filter (transform output)
         │
         ▼
[6] LLM Provider Router
         │
         ├── Ollama: /ollama/* → http://ollama:11434/api/chat
         ├── OpenAI: /openai/* → api.openai.com/v1/chat/completions
         ├── Azure:  → Azure OpenAI endpoint
         └── Anthropic → api.anthropic.com/v1/messages
         │
         ▼
[7] Stream response via Socket.IO → Frontend
         │
         ▼
[8] Simpan message ke database (chats table)
```

### 2.2 Entry Point - main.py

```python
# backend/open_webui/main.py

from fastapi import FastAPI
from open_webui.apps.factory import create_app

# create_app() adalah factory pattern yang return FastAPI instance
app: FastAPI = create_app()

# Lifespan: init DB, start Redis listener, register Socket.IO
# Static files: serve SvelteKit build dari /app/build
# Routes: semua 31 router di-register di sini
# WebSocket: /ws endpoint via python-socketio
```

---

## 3. RAG Pipeline (Upload Dokumen → Tanya Jawab)

### 3.1 Alur Lengkap (ASCII)

```
┌──────────────────────────────────────────────────────────────────┐
│                    RAG - INDEXING PHASE                           │
│                  (Upload Dokumen ke Vector DB)                    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
[1] User upload file di Knowledge Base UI
         │
         ▼
[2] POST /api/v1/retrieval/upload
         │
         ▼
[3] save_docs_to_vector_db() di retrieval.py
         │
         ├── [3a] Deduplication: hash file, cek sudah di-index?
         │
         ├── [3b] Content Extraction:
         │        ├── PDF       → PyMuPDF, Marker (DL)
         │        ├── YouTube   → youtube-transcript-api
         │        ├── Web       → Playwright / Trafilatura
         │        ├── Office    → python-docx, openpyxl
         │        ├── Image     → Mistral OCR / PaddleOCR
         │        └── Audio     → Whisper transcription
         │
         ├── [3c] Chunking:
         │        ├── RecursiveCharacterTextSplitter (default)
         │        ├── TokenTextSplitter (tiktoken)
         │        ├── MarkdownHeaderTextSplitter (preserve header)
         │        └── Config: CHUNK_SIZE=1000, CHUNK_OVERLAP=100
         │
         ├── [3d] Metadata Enrichment:
         │        └── Source name, page number, headings, tags
         │
         ├── [3e] Embedding Generation:
         │        ├── SentenceTransformers (default: all-MiniLM-L6-v2)
         │        ├── OpenAI ada-002 / text-embedding-3
         │        ├── Ollama (nomic-embed-text) ✅ ← PAKAI INI
         │        └── Azure OpenAI embeddings
         │
         └── [3f] Vector DB Insertion:
                  ├── ChromaDB (default, in-process)
                  ├── Collection: knowledge_{knowledge_id}
                  └── Chroma client: /app/backend/data/chroma
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   RAG - RETRIEVAL PHASE                          │
│                  (Query Dokumen untuk Jawaban)                    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
[1] User kirim pesan dengan konteks knowledge
         │
         ▼
[2] POST /api/v1/retrieval/query
         │
         ├── [2a] Embed query dengan model yang sama
         │
         ├── [2b] Vector similarity search (top-K)
         │         K = RAG_TOP_K (default: 5)
         │
         ├── [2c] Hybrid Search (optional):
         │         ├── BM25 keyword search
         │         └── Reciprocal Rank Fusion (RRF)
         │
         ├── [2d] Reranking (optional):
         │         ├── Cohere Rerank
         │         ├── FlashRank (local, open-source)
         │         └── OpenAI reranking
         │
         └── [2e] Context Assembly:
                  ├── Format: "Source: {name}, Page {page}\n\n{content}"
                  ├── Trim ke RAG_CONTEXT_MAX_TOKENS (8192)
                  └── Inject ke system prompt
                           │
                           ▼
[3] Gabung dengan chat message → Kirim ke LLM
         │
         ▼
[4] LLM generate jawaban dengan konteks dokumen
         │
         ▼
[5] Response + source reference → User
```

### 3.2 Konfigurasi .env untuk RAG

```env
#Embedding Engine - GUNAKAN OLLAMA (lokal, gratis)
RAG_EMBEDDING_ENGINE=ollama
RAG_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434

# Chunking
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=100

# Vector DB (default: ChromaDB)
VECTOR_DB=chroma1
PERSIST_DIRECTORY=/app/backend/data/chroma

# Optional: Hybrid Search
ENABLE_RAG_HYBRID_SEARCH=false
RAG_FUSION_ALPHA=0.5

# Optional: Reranking
ENABLE_RAG_RERANKING=false
RAG_RERANKING_MODEL=..
```

### 3.3 Key RAG Files

| File | Line | Purpose |
|------|------|---------|
| `routers/retrieval.py` | ~3460 | RAG API: upload, query, web search |
| `retrieval/utils.py` | ~1400 | get_embedding_function, get_reranking_function |
| `retrieval/loaders/` | (dir) | PDF, YouTube, Web, Office loader |
| `retrieval/vector/` | (dir) | ChromaDB, pgvector, Qdrant, dll |

---

## 4. Chat Pipeline

### 4.1 Chat Completions Flow

```python
# routers/ollama.py + routers/openai.py
# POST /api/v1/chat/completions

async def generate_chat_completion(request: ChatCompletionRequest):
    """
    1. Auth: JWT token verification
    2. Pipeline/Inlet: transform input
    3. Model selection: dari request atau user settings
    4. Ollama: POST /ollama/api/chat
       OpenAI: POST /openai/v1/chat/completions
    5. Stream: token-by-token via Socket.IO
    6. Pipeline/Outlet: transform output
    7. Save: chat message ke database
    """
```

### 4.2 WebSocket Streaming

```
Frontend (Socket.IO Client)
    │
    │ connect(user_id, JWT_token)
    ▼
/backend/socket.io/  (python-socketio)
    │
    ├── Rooms:
    │    ├── user:{user_id}    → private events
    │    ├── channel:{id}      → group chat
    │    └── note:{id}        → collaborative notes
    │
    ├── Events:
    │    ├── connect / disconnect
    │    ├── events:chat       → chat streaming
    │    ├── events:channel   → channel messages
    │    └── ydoc:*           → Yjs collaborative editing
    │
    └── Optional: Redis pub/sub (multi-instance scaling)
```

---

## 5. Ollama Integration

### 5.1 Ollama Router Architecture

```
/ollama/*           → Ollama native API
/ollama/v1/*        → OpenAI-compatible API
/ollama/v1/messages → Anthropic Messages API
/ollama/v1/responses → OpenAI Responses API
```

### 5.2 Supported Endpoints

| Endpoint | Ollama Path | Purpose |
|----------|-------------|---------|
| `GET /ollama/api/tags` | `/api/tags` | List available models |
| `POST /ollama/api/chat` | `/api/chat` | Chat completion |
| `POST /ollama/api/embed` | `/api/embed` | Generate embeddings |
| `POST /ollama/api/pull` | `/api/pull` | Pull model |
| `DELETE /ollama/api/delete` | `/api/delete` | Delete model |

### 5.3 Ollama Config

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=                           # Optional
OLLAMA_REQUEST_TIMEOUT=120
OLLAMA_TEMPERATURE=0.8
OLLAMA_TOP_P=0.9
OLLAMA_NUM_CTX=4096
OLLAMA_KEEP_ALIVE=5m
```

### 5.4 Model yang Kamu Punya

| Model | Size | Best For |
|-------|------|----------|
| `qwen2.5:7b` | 4.7 GB | **Terbaik** - chat umum, konteks panjang |
| `phi3:3.8b` | 2.2 GB | Reasoning, coding |
| `qwen2.5:3b` | 1.9 GB | Balanced, cepat |
| `gemma2:2b` | 1.6 GB | Ringan, cukup bagus |
| `nomic-embed-text` | 274 MB | **Embedding untuk RAG** |

---

## 6. Database & Model

### 6.1 ORM Models

```
backend/open_webui/models/
├── users.py       → User accounts, profiles, permissions
├── chats.py       → Chat sessions, message history, search
├── documents.py   → File metadata untuk knowledge bases
├── memories.py    → Persistent user memories
├── channels.py    → Multi-user group chats
├── folders.py    → Folder hierarchy
├── tools.py      → Tool server registry
├── functions.py  → Pipeline functions
└── configs.py    → System configuration
```

### 6.2 Chat Model Schema

```python
class Chat(Base):
    id: str              # UUID
    user_id: str         # FK ke users
    title: str
    share_id: str | None  # Public share link

    history: List[dict]  # Array message objects
    # [{ "role": "user", "content": "..." },
    #  { "role": "assistant", "content": "..." }]

    models: List[str]    # Models yang dipakai
    tags: List[str]

    archived: bool
    pinned: bool
```

### 6.3 Database Options

| Type | Config | Use Case |
|------|--------|----------|
| SQLite | Default | Development, small scale |
| PostgreSQL | `DATABASE_URL=postgresql+asyncpg://...` | Production |
| SQLite + encryption | `DATABASE_URL=sqlite+aiosqlite://...?cipher=...` | Encrypted at rest |

---

## 7. Key Files Reference

### Backend

| File | Purpose |
|------|---------|
| `backend/open_webui/main.py` | FastAPI app factory, lifespan, route registration |
| `backend/open_webui/env.py` | Environment variable resolution |
| `backend/open_webui/config.py` | Runtime config, all feature flags |
| `backend/open_webui/routers/ollama.py` | Ollama proxy + OpenAI-compatible |
| `backend/open_webui/routers/openai.py` | OpenAI API proxy + Azure + Anthropic |
| `backend/open_webui/routers/retrieval.py` | RAG pipeline |
| `backend/open_webui/routers/auths.py` | Auth: login, OAuth, LDAP, API key |
| `backend/open_webui/routers/chats.py` | Chat CRUD, history, sharing |
| `backend/open_webui/socket/main.py` | Socket.IO server, Yjs, session pool |
| `backend/open_webui/utils/chat.py` | Chat completion orchestration |

### Frontend

| File | Purpose |
|------|---------|
| `src/routes/(app)/+page.svelte` | Main chat UI |
| `src/lib/apis/index.ts` | API client untuk semua backend call |
| `src/lib/constants.ts` | API base URLs, constants |
| `src/lib/components/chat/Chat.svelte` | Core chat component |

### Docker

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage: Node.js → Python |
| `docker-compose.yaml` | Ollama + Open WebUI |
| `backend/start.sh` | Container entry point |

---

## 8. Setup Guide

### 8.1 Docker (Recommended)

```powershell
# 1. Clone / masuk ke folder
cd D:\PENTING\open-webui-main

# 2. Buat .env
copy .env.example .env

# 3. Edit .env
#    OLLAMA_BASE_URL=http://localhost:11434
#    WEBUI_SECRET_KEY=rahasia-kamu
#    RAG_EMBEDDING_ENGINE=ollama
#    RAG_EMBEDDING_MODEL=nomic-embed-text

# 4. Build & run
docker compose up -d

# 5. Akses
#    http://localhost:3000
```

### 8.2 Local Development (Windows)

**Backend:**
```powershell
cd D:\PENTING\open-webui-main\backend

# Virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Buat .env
copy ..\.env.example ..\.env
# Edit ..\.env

# Run
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --reload
```

**Frontend (terminal terpisah):**
```powershell
cd D:\PENTING\open-webui-main
npm install --force
npm run dev
```

**Akses:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8080

### 8.3 Environment Variables Quick Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `RAG_EMBEDDING_ENGINE` | `sentence-transformers` | Embedding engine |
| `RAG_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `VECTOR_DB` | `chroma` | Vector database |
| `RAG_CHUNK_SIZE` | `1000` | Text chunk size |
| `WEBUI_AUTH` | `true` | Enable auth |
| `WEBUI_SECRET_KEY` | (auto) | JWT signing key |
| `CORS_ALLOW_ORIGIN` | `*` | CORS origins |
| `DATABASE_URL` | SQLite | Database connection |
| `WEBSOCKET_MANAGER` | (in-memory) | `redis` for scaling |

---

## Quick Command Reference

```bash
# Pull model Ollama
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# List models
ollama list

# Test Ollama API
curl http://localhost:11434/api/tags

# Test backend health
curl http://localhost:8080/health

# Check running models
curl http://localhost:11434/api/ps
```
