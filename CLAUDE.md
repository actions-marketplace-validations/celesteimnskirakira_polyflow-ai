# Polyflow — Project Direction for AI Agents

## What This Is

Polyflow is a CLI tool and GitHub Action that runs Claude, Gemini, and GPT-4 **in parallel on the same task** — they cross-validate each other, vote on findings, and synthesize a final answer. Defined in a single YAML file.

**The core insight:** No single AI model is right 100% of the time. But when multiple models agree, that's a signal worth trusting. When they disagree, that's where the real problems are. This is **multi-model consensus** — the same principle behind ensemble methods in ML, applied to developer workflows.

The workflow it automates: developers manually copying prompts to multiple AI services ("Model Musical Chairs" — Addy Osmani, Google). Polyflow makes this a YAML file you run in one command, fully automated, no human approval needed.

```bash
pip install polyflow-ai
polyflow run code-review-multi-model -i "$(git diff HEAD~1)"
```

---

## The Unique Combination (Our Moat)

No other tool has all five of these simultaneously:

| Feature | Why it matters |
|---|---|
| **Parallel multi-model execution** | Claude + Gemini + GPT-4 on the same prompt simultaneously — true concurrency via asyncio.gather |
| **Multi-model consensus/aggregation** | `mode: vote` surfaces what all models agree on; `mode: diff` shows where they disagree |
| **YAML-declarative workflows** | Version-controllable, shareable, diff-able — not Python code |
| **GitHub Action (`action.yml`)** | One `uses:` line in any repo to get consensus AI reviews on every PR |
| **`pip install` CLI + `--ci` mode** | Works headlessly in terminals, scripts, and CI/CD with zero human intervention |

**HITL (Human-in-the-Loop)** exists as an optional primitive for decisions that require explicit human authority — not because humans are smarter, but for accountability and control. It is NOT the primary differentiator.

The closest competitors: OpenClaw (single model, no CI/CD, security vulnerabilities), LangChain (Python boilerplate, no parallel multi-model), CodeRabbit/BugBot/Graphite (single model, SaaS pricing, no YAML).

---

## Target User

**Primary:** A developer who uses AI for code review, security audits, or workflow automation and is frustrated that:
1. Every AI tool only uses one model
2. Getting multi-model results requires copy-pasting the same prompt manually
3. CI/CD AI integration requires writing glue code

**Secondary:** Teams that want AI-powered PR review without paying $20-40/user/month for single-model SaaS tools.

---

## Architecture

```
src/polyflow/
  cli.py              Entry point — all Click commands (run, list, validate, new, doctor...)
  config.py           API key loading (OPENROUTER_API_KEY, ANTHROPIC_API_KEY, etc.)
  schema/
    workflow.py       Pydantic v2 models for the YAML schema (Workflow, Step, HitlConfig...)
  engine/
    runner.py         Top-level workflow executor — loads YAML, loops steps, handles output
    executor.py       Step execution — sequential, parallel (asyncio.gather), retry/backoff
    template.py       Jinja2-style template rendering ({{input}}, {{steps.x.output}}, pipes)
    hitl.py           Human-in-the-Loop terminal prompts
    context_builder.py  File injection (inject_cwd, inject_files globs)
  models/
    openrouter.py     OpenRouter adapter (recommended — covers all models with one key)
    claude.py         Anthropic SDK direct adapter
    gemini.py         google-genai SDK adapter
    openai_model.py   OpenAI SDK adapter
    base.py           Abstract base class
  registry/
    client.py         Community workflow registry (pull, search commands)

workflows/examples/   22 built-in workflows shipped with the package
action.yml            GitHub Action composite action
```

---

## Development Priorities

### P0 — Core stability (do not break)
- `polyflow run` with parallel steps + `aggregate.mode: vote/diff/summary`
- OpenRouter adapter (most users will use this)
- `--ci` flag (used by GitHub Action, enables headless execution)
- `action.yml` (GitHub Action)

### P1 — Next features (Issues already filed)
- `type: loop` — iterative PDCA loops with termination condition ([#1](https://github.com/celesteimnskirakira/polyflow-ai/issues/1))
- `type: shell` — local command execution for full PDCA automation ([#2](https://github.com/celesteimnskirakira/polyflow-ai/issues/2))

### P2 — Growth
- GitHub Marketplace listing (`action.yml` is ready — submit now)
- `polyflow-mcp` — MCP server so Polyflow can be called from GitHub Agentic Workflows
- More built-in workflows showcasing multi-model consensus
- Workflow registry (`polyflow pull <name>`) as community grows

---

## What NOT to Build

- **A GUI or web interface** — CLI-first is the positioning. Keep it.
- **An autonomous agent** — That's OpenClaw. Polyflow is declarative and auditable.
- **A SaaS platform** — Open source + GitHub Action is the distribution strategy.
- **Single-model workflows** — Every new built-in workflow should use at least 2 models with aggregation. Single-model is what every other tool already does.
- **HITL as a selling point** — HITL is a useful primitive but not the differentiator. Lead with consensus, mention HITL as optional control.

---

## Key Design Decisions

**Why multi-model consensus instead of single-model?**
No model is right 100% of the time. Multiple models checking the same thing surfaces blind spots no single model has. `mode: vote` = high-confidence findings. `mode: diff` = where to pay attention. This is ensemble learning applied to developer workflows.

**Why YAML over Python DSL?**
YAML workflows are version-controllable, PR-reviewable, and writable by non-engineers. Python DSLs (LangChain, CrewAI) require 80+ lines of boilerplate for what Polyflow does in 20 lines of YAML.

**Why OpenRouter as default?**
One API key covers Claude + Gemini + GPT-4. Reduces friction from 3 signups to 1.

**Why `--ci` mode?**
Polyflow runs fully headlessly in CI/CD. HITL is optional. `--ci` auto-approves any HITL checkpoint, so all workflows work in GitHub Actions without modification.

**Why HITL at all?**
For high-stakes decisions where you want explicit human authority — not because the human knows more, but because accountability matters. Deploy to prod, delete data, send external communication. Always optional, never required for technical workflows.

---

## Promotion Context

- Published on PyPI as `polyflow-ai` (package name `polyflow` was taken)
- GitHub repo: `celesteimnskirakira/polyflow-ai`
- Target: GitHub stars + resume material
- Key angle: "First tool to automate Model Musical Chairs in a GitHub Action"
- HackerNews Show HN is the highest-leverage channel for initial stars
- GitHub Marketplace submission (action.yml ready) is the long-tail channel

---

## Running Tests

```bash
# Unit tests (no API key needed)
pytest tests/ -k "not integration"

# All tests (requires OPENROUTER_API_KEY)
pytest tests/

# Validate a workflow YAML
polyflow validate workflows/examples/code-review-multi-model.yaml
```

Tests cover: schema validation, template rendering, executor logic (retry/backoff, parallel failures, aggregate.model), HITL, CLI commands.
