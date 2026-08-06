# rag/ — Retrieval Architecture (Person 3)

## What's in here

| File | Purpose |
|------|---------|
| `sync_policies.py` | Copies the policy markdown files from `mcp_server/` (the authoritative source, also exposed as MCP resources) into `rag/policies/`. Run this whenever a source policy changes instead of copying files manually. |
| `policies/` | Snapshot of the RAG corpus containing the IronBridge policy documents. Files are split by `##` section headers using LangChain's `MarkdownHeaderTextSplitter`, with `RecursiveCharacterTextSplitter` as a fallback for oversized sections. |
| `chunking.py` | `get_policy_chunks()` reads every policy file, splits it into section-based chunks, and attaches metadata such as source filename and section title. |
| `vector_store.py` | `setup_vector_store()` embeds every chunk using FastEmbed (`BAAI/bge-small-en-v1.5`), stores vectors in a local Qdrant collection (`ironbridge_policies`), and creates payload indexes for metadata filtering. |
| `test_search.py` | Demonstrates filtered similarity search using Qdrant metadata filters to restrict retrieval to selected source documents. |

---

## Design Decisions

### FastEmbed instead of OpenAI Embeddings
- Runs completely locally.
- No API key required.
- No per-query cost.
- More than sufficient for the current small policy corpus.

### Section-based chunking instead of fixed-size chunking
- IronBridge policy documents are short.
- Splitting by Markdown headers (`##`) preserves logical sections.
- Each chunk receives meaningful metadata (section title + source file).

### `rag/policies/` is a generated snapshot
- `mcp_server/*.md` remains the single source of truth.
- `sync_policies.py` copies the files automatically so the RAG corpus always matches the MCP resources.

### Local Qdrant storage
- The local database (`rag/local_qdrant/`) is regenerated when needed.
- It is excluded from Git using `.gitignore`.

---

## Setup

```bash
pip install -r rag/requirements.txt

python rag/sync_policies.py
python -m rag.vector_store
python rag/test_search.py
```

---

## Status / Next Steps

- [x] Bug fixes (#5 and #6)
- [x] Section-aware chunking
- [x] Local Qdrant vector database
- [x] Metadata payload indexing
- [ ] Hybrid Search (Vector + BM25)
- [ ] Agentic RAG
- [ ] Self-RAG verification (integration with Person 1)
- [ ] `retrieval_eval/` benchmark and comparison table
