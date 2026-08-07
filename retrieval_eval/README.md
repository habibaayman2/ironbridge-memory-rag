# retrieval_eval/

Retrieval architecture evaluation for the IronBridge Procurement Assistant.

## What this solves

IronBridge staff ask the assistant questions that span multiple policy
documents and require both exact identifiers ("Policy #2") and
multi-part reasoning ("handling requirements AND approval workflow").
This folder measures which retrieval architecture actually answers those
questions correctly, at what cost, so the choice of shipped architecture
is justified by numbers rather than intuition.

## Structure

```
retrieval_eval/
├── test_questions.py   # Fixed question set (≥1 per architecture)
├── evaluate.py         # Runs all 3 architectures, prints comparison table
├── results.json        # Generated artifact (not committed)
└── README.md           # This file
```

## The test questions

| ID | Favored Architecture | Why |
|----|----------------------|-----|
| `naive_001` / `naive_002` | Naive RAG | General semantic questions; embeddings alone suffice. |
| `hybrid_001` / `hybrid_002` | Hybrid RAG | Exact identifiers ("Policy #2", "50kg") that BM25 catches better than pure vectors. |
| `agentic_001` / `agentic_002` | Agentic RAG | Multi-part questions spanning two+ policy docs; needs a second retrieval hop. |

The set is **fixed** — changing questions mid-run invalidates the comparison.

## Running the evaluation

```bash
# from the repo root
python -m retrieval_eval.evaluate
```

Requirements:
- `GROQ_API_KEY` exported (all three architectures use Groq for generation).
- Vector store already built (`rag/vector_store.py` will reuse the existing Qdrant collection).

## Output

Terminal table (markdown) + `results.json` with per-question breakdown.

## Which architecture we ship

**Agentic RAG** — because IronBridge's real query pattern is multi-part
policy questions, and Agentic is the only architecture that can recover
from an incomplete first retrieval by issuing a second, more targeted
query. The comparison table quantifies the cost (latency, tokens) of
that extra hop so the decision is explicit, not assumed.
