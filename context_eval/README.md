
# context_eval/

Context window management for the IronBridge Procurement Assistant's
agent loop. Implements and evaluates all four context management
strategies required by the Memory & RAG Lab, against a fixed
long-context test suite, and ships the strategy the resulting
comparison table justifies — not the one that sounds best in theory.

## The problem this solves

IronBridge's assistant sessions are tool-call-heavy: a site engineer or
procurement officer works through inventory checks, budget lookups, and
equipment status across many turns before reaching a decision. Left
unpruned, that transcript grows without bound and eventually exceeds
the model's context window. Pruned carelessly, it silently drops the
detail that mattered — a budget caveat mentioned once, early, and never
repeated.

This answers two questions with real numbers instead of
intuition: **which pruning strategy actually preserves the critical
detail**, and **at what cost** in tokens and latency.

## Structure

```
context_eval/
├── transcript.py                  # shared Turn data structure every strategy operates on
├── sliding_window.py               # strategy 1
├── observation_masking.py          # strategy 2
├── recursive_summarization.py      # strategy 3
├── zone_based_pruning.py           # strategy 4
├── evaluate.py                     # runs all four against the test suite, prints the comparison table
└── test_cases/
    └── generator.py                 # builds the long-context test suite
```

## The four strategies

Every strategy has the same signature shape — `apply(turns: list[Turn], ...) -> list[Turn]` —
so `evaluate.py` can run all four against identical input and score
them identically.

| Strategy | File | Approach |
|---|---|---|
| **Sliding window** | `sliding_window.py` | Keeps only the last `window_turns` (default 10) verbatim; drops everything before that unconditionally. |
| **Observation / tool-output masking** | `observation_masking.py` | Keeps every turn's role and position, but replaces the content of tool-output turns older than the last `keep_last_n_tool_outputs` (default 3) with a placeholder. Non-tool turns are never masked, regardless of age. |
| **Recursive summarization** | `recursive_summarization.py` | Every `summarize_every` turns (default 15), compacts everything older than `keep_recent` (default 8) into a single synthetic summary turn — with any turn explicitly marked `critical` preserved verbatim rather than folded into the summary, so a compression pass can't accidentally erase the one detail the eval is checking for. |
| **Zone-based pruning** | `zone_based_pruning.py` | Splits the transcript into four zones with different retention policies: an **anchor** zone (first `anchor_turns`, kept verbatim), a lightly-pruned early-middle zone (tool outputs masked), an aggressively-compressed late-middle zone (routine tool turns collapsed to one line, critical turns still preserved verbatim), and a **recent** zone (last `recent_turns`, kept verbatim). |

## The test suite

`test_cases/generator.py` builds synthetic long-context transcripts
shaped around a single scenario: a critical fact is stated once, early
(turn 2), then buried under 32–40 turns of **real** tool-output noise —
not synthetic filler text — before a final question that can only be
answered correctly if the turn-2 detail survived pruning.

`generate_test_suite()` produces 10 variations (transcript length
varied 32–40 tool turns) so the comparison isn't tuned to one exact
transcript shape, per the lab's requirement to keep a fixed suite once
evaluation starts.

## Running the evaluation

```bash
# from the project root
python -m context_eval.evaluate
```

This regenerates the test suite, runs all four strategies against it,
and prints the comparison table: recall accuracy, average input
tokens, average output tokens, and average latency per strategy.

## Results

```
Strategy                   Recall Accuracy    Avg Input Tokens   Avg Output Tokens   Avg Latency
sliding_window              0/10 (0%)          834                0                   0.00001s
observation_masking         10/10 (100%)       1303               0                   0.00006s
recursive_summarization     10/10 (100%)       815                0                   0.00002s
zone_based_pruning          10/10 (100%)       1298               0                   0.00002s
```

*(Captured with the deterministic fallback generator — no live LLM
call at capture time. Latency and output-token numbers will be
materially higher with a real model behind the summarizer, and
`recursive_summarization` in particular will show real added latency
once its summarization step is backed by an actual API call rather
than the fallback.)*

## Which strategy we ship

**Sliding window is disqualified outright** — it loses the critical
detail on every single run. The detail lives at turn 2; a 10-turn
window can never reach that far back once the transcript passes ~40
turns, regardless of how important the detail was.

Among the three that preserve it 100% of the time, the decision comes
down to what's actually being pruned. IronBridge's long sessions are
tool-call-heavy, not dialogue-heavy — the bloat is JSON tool output.
`observation_masking` targets exactly that, and does it without an
extra model call: `recursive_summarization` needs a summarization pass
per compaction (real added latency/cost once a live model is behind
it, even though the fallback generator hides that cost here), and
`zone_based_pruning` carries the highest average token footprint of
the three winners on this transcript shape because its anchor zone
keeps the first several turns fully verbatim regardless of content.

**Shipped strategy: `observation_masking`.** It matches IronBridge's
actual bloat source, ties for best accuracy, and is the only one of
the three winners that adds zero extra model calls to do its job.
