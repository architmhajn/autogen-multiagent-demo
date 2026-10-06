# AutoGen Multi-Agent Demo

A working implementation of the GroupChat pattern described in **Section 5
(Reference Implementation Pattern)** of the benchmark report
*"AutoGen (Microsoft) — A Benchmark-Oriented Study..."* (TAE-1, UNAIL411).

## What it does

Five conversable agents collaborate in a `GroupChat`, matching the roles
analysed against each of the five benchmarks in the report:

| Agent | Role | Benchmark relevance (per report §4) |
|---|---|---|
| `Human` (UserProxyAgent) | Human-in-the-loop checkpoint | — |
| `Assistant` | Interprets the request, drafts a plan | MMLU / GPQA breadth |
| `Coder` | Writes code to satisfy the plan | HumanEval / SWE-bench Verified |
| `Executor` | Runs the code, returns stdout/stderr | Closes the execute-and-observe loop (§4.3) |
| `Critic` | Reviews output before it's finalised | TruthfulQA-aware check (§4.5) |

The `GroupChatManager` performs LLM-based speaker selection — the same
component the report flags in Section 7 as the reason Microsoft moved
production workloads to the typed-graph Microsoft Agent Framework instead.

## Setup

```bash
pip install -r requirements.txt
```

Then open `config.py` and fill in **one** of the three backend options:

1. **OpenAI** — set the `OPENAI_API_KEY` environment variable, or paste the
   key directly into `OPENAI_CONFIG`.
2. **Azure OpenAI** — fill in your resource URL, deployment name, and key
   in `AZURE_CONFIG`, then set `LLM_CONFIG = AZURE_CONFIG` at the bottom of
   the file.
3. **Local model via Ollama** — install [Ollama](https://ollama.com), run
   `ollama pull llama3.1` (or any model you prefer), then set
   `LLM_CONFIG = OLLAMA_CONFIG`. No API key required.

## Run

```bash
python main.py "Write a function that finds the first repeated element in a list."
```

Or run with no arguments to use the built-in palindrome-check demo task.

## How this maps to the report

- The **Coder → Executor** loop is the concrete version of the
  "execute-and-observe loop" described in report Section 4.3 (HumanEval):
  code is generated, run, and any error trace is fed back for revision.
- The **Planner(Assistant) → Coder → Executor → Critic** sequence is the
  exact pattern Section 4.4 calls "structurally closest" to what
  SWE-bench Verified evaluates.
- The **Critic** agent is the practical analogue of the TruthfulQA check
  discussed in Section 4.5 — it challenges claims before they reach the
  human checkpoint, rather than relying on the underlying model's
  intrinsic honesty.
- Per Section 4 and the report's conclusion, you can bind each agent to a
  *different* model in `config.py` (e.g. a high-GPQA model for `Critic`, a
  high-HumanEval model for `Coder`) rather than using one model everywhere.

## Notes

- `use_docker` is set to `False` in `agents.py` for convenience. For any
  untrusted code, set it to `True` and ensure Docker is running — this
  sandboxes execution instead of running code directly on your machine.
- `max_round=12` caps the conversation length; raise it for harder tasks.
- This demo uses the **AG2** fork (`pip install ag2`), which preserves the
  legacy v0.2-style `GroupChat` API discussed in report Section 2 and
  Section 9, since original AutoGen has been in maintenance mode since
  October 2025.
