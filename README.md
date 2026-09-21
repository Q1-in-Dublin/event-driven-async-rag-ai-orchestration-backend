# Event-Driven Async RAG Orchestration Backend

A complete AI system where a single Slack message triggers a full production pipeline: signature verification → async queue → LangGraph orchestration → vector search → real LLM → Slack response.

**Example**: User asks "@RAG Bot What's the vacation policy?" in Slack → system searches pgvector for policy documents → Gemini LLM generates answer → responds in Slack

---

## Architecture

```
Slack
  ↓
FastAPI /slack/events (signature verification)
  ↓
Redis Streams (XADD)
  ↓
Worker (XREADGROUP)
  ↓
LangGraph Workflow
  ├─ ClassifyIntent (needs RAG?)
  ├─ EmbedQuery (vectorize question)
  ├─ SearchVectorDB (pgvector search)
  ├─ BuildPrompt (add context)
  ├─ CallLLM (Gemini 3.5 Flash)
  ├─ SaveResult (persist to DB)
  └─ RespondToSlack (send via Slack API)
  ↓
Slack (response delivered)
```

---

## Status: Complete ✅

**Phase 1: Event-Driven Pipeline**

- ✅ FastAPI with async handlers
- ✅ Redis Streams (consumer groups, XACK for at-least-once delivery)
- ✅ PostgreSQL with pgvector
- ✅ LangGraph state machine with conditional branching

**Phase 2: Production Hardening (All Done!)**

- ✅ Slack webhook signature verification (HMAC-SHA256 + timestamp validation)
- ✅ API Key authentication (Bearer token with timing-attack protection)
- ✅ Real Slack integration via webhook
- ✅ Real Gemini 3.5 Flash LLM (not mock)
- ✅ pgvector RAG (6 sample documents loaded)
- ✅ Slack response delivery via chat.postMessage
- ✅ 9/9 automated tests passing
- ✅ End-to-end validated: Slack → LLM → Slack (live)

---

## Tech Stack

| Layer         | Choice           | Why                                                     |
| ------------- | ---------------- | ------------------------------------------------------- |
| API           | FastAPI          | Modern async Python framework with automatic docs       |
| Queue         | Redis Streams    | Consumer groups + XACK = zero message loss              |
| Orchestration | LangGraph        | Explicit state graphs for complex workflows             |
| Vector DB     | pgvector         | Semantic search inside PostgreSQL (no external deps)    |
| LLM           | Gemini 3.5 Flash | Real Agent Platform integration                         |
| Security      | HMAC + API Key   | Webhook verification + internal endpoint protection     |
| Tests         | pytest           | 9 automated tests (unit + integration)                  |
| Local Stack   | Docker Compose   | FastAPI + Redis + PostgreSQL (complete dev environment) |

---

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Add: GOOGLE_CLOUD_PROJECT, SLACK_BOT_TOKEN to .env

# 2. Run
docker-compose up -d

# 3. Test in Slack
@RAG Bot What's the vacation policy?

# 4. API Docs
http://localhost:8000/docs
```

---

## Project Structure

```
app/
├── main.py              # FastAPI endpoints
├── auth/                # Slack signature verification, API key auth
├── queue/               # Redis Streams producer/consumer
├── graph/               # LangGraph workflow nodes
├── rag/                 # Embedding + pgvector search
├── llm/                 # Gemini LLM client
├── db/                  # SQLAlchemy ORM models
└── config.py

tests/                   # 9 automated tests (all passing)
docker-compose.yml       # Local stack
```

---

## Key Learning

- **Event-Driven Async**: 202 Accepted pattern (fast response, background processing)
- **Redis Streams**: Consumer groups for reliable message delivery
- **LangGraph**: State machines for complex workflows
- **pgvector**: Vector search in PostgreSQL
- **Security**: HMAC verification + timing-attack protection
- **Real LLM**: Gemini 3.5 Flash integration

---

## Results

✅ **Complete E2E System Working**  
✅ **Slack → Gemini AI → Slack (Real-time)**  
✅ **9/9 Tests Passing**  
✅ **590 Lines of Code (Efficient)**  
✅ **Production-Ready**
