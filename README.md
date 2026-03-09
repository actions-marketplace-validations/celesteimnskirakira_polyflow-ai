# Polyflow

[![PyPI version](https://img.shields.io/pypi/v/polyflow-ai.svg)](https://pypi.org/project/polyflow-ai/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Multiple models check the same thing. Consensus beats any single AI.**

Run any combination of AI models in parallel on the same task — they cross-validate each other, vote on findings, and synthesize a final answer. No single model's blind spots. Describe what you want in plain English, or write a YAML file.

```bash
pip install polyflow-ai
export OPENROUTER_API_KEY=sk-or-...

# Use a built-in workflow
polyflow run code-review-multi-model -i "$(git diff HEAD~1)"

# Or generate one from natural language
polyflow new "multiple models audit my API for security issues, vote on findings"
```

Add to any repo as a GitHub Action — every PR reviewed automatically:

```yaml
- uses: celesteimnskirakira/polyflow-ai@v1
  with:
    workflow: code-review-multi-model
    input: ${{ steps.diff.outputs.content }}
    openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}
```

---

## Why multiple models?

No model is right 100% of the time. But when multiple models **all agree**, that's a signal worth trusting. When they disagree, that's where the real problems are.

```
Single model:    Claude says "no security issues"   → might have blind spots

Multiple models: Claude says "no security issues"
                 Gemini finds SQL injection          → consensus surfaces the real finding
                 GPT-4 finds missing auth check
                 Claude synthesizes final report
```

This is **ensemble learning applied to developer workflows** — the same principle behind code review, peer review, and ML ensembles.

---

## Install

```bash
pip install polyflow-ai
```

Requires Python 3.11+. One key covers all models:

```bash
export OPENROUTER_API_KEY=sk-or-...    # openrouter.ai — 290+ models, one key
polyflow doctor                         # verify setup
```

---

## Quick Start

```bash
# Browse 22 built-in workflows
polyflow list
polyflow list --tag security

# Run a workflow
polyflow run code-review-multi-model -i "$(git diff HEAD~1)"
polyflow run security-audit -i "$(cat src/auth.py)"
polyflow run bug-triage -i "TypeError: 'NoneType' object is not subscriptable"

# Generate a custom workflow from natural language
polyflow new "multiple models review my API design, vote on findings" -o api-review.yaml
polyflow run ./api-review.yaml -i "$(cat src/api.py)"

# Run headlessly in CI/CD
polyflow run <workflow> --ci -i "..."
```

---

## How It Works

Send the same prompt to multiple models in parallel, then aggregate:

```yaml
name: security-consensus

steps:
  - id: audit
    type: parallel
    steps:
      - id: claude
        model: claude
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
      - id: gemini
        model: gemini
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
      - id: gpt4
        model: gpt-4
        prompt: "Find security vulnerabilities (OWASP Top 10): {{input}}"
    aggregate:
      mode: vote       # only findings all models agree on
      model: claude    # Claude writes the final report
      prompt: |
        Multiple models independently audited this code.
        Mark consensus findings as HIGH CONFIDENCE, disagreements as NEEDS REVIEW.
        {{aggregated}}

output:
  format: markdown
  save_to: security-report.md
```

| Aggregate mode | When to use |
|---|---|
| `vote` | Highest confidence — only what all models agree on |
| `diff` | Show where models disagree — good for exploring trade-offs |
| `summary` | One model synthesizes all outputs into a single report |
| `raw` | Return all outputs separately |

Chain steps for sequential pipelines:

```yaml
steps:
  - id: find_issues
    type: parallel
    steps: [...]
    aggregate:
      mode: vote
      model: claude

  - id: generate_fix
    model: claude
    prompt: |
      Consensus issues: {{steps.find_issues.output}}
      Write a fix for each HIGH CONFIDENCE issue.
      Code: {{input}}
```

---

## Customize

### Use any model

Any [OpenRouter model ID](https://openrouter.ai/models) works directly in YAML:

```yaml
model: claude          # Claude Sonnet 4.6 (default)
model: gemini          # Gemini 2.0 Flash
model: gpt-4           # GPT-4o
model: claude-opus     # Claude Opus 4.6 (premium)
model: gpt-5           # GPT-5.4 (premium)
model: deepseek/deepseek-r2          # any OpenRouter model ID
model: meta-llama/llama-3.3-70b-instruct
```

### Change the number of models

Edit the `steps` list inside a `type: parallel` block — add or remove sub-steps freely:

```yaml
- id: review
  type: parallel
  steps:
    - id: model_a
      model: claude
      prompt: "Review: {{input}}"
    - id: model_b
      model: gemini
      prompt: "Review: {{input}}"
    # add more models here
  aggregate:
    mode: diff
    model: claude
```

### Change aggregate mode

```yaml
aggregate:
  mode: vote       # vote | diff | summary | raw
  model: claude    # which model writes the synthesis (optional)
  prompt: |        # custom synthesis prompt (optional)
    Summarize findings. Mark consensus items as HIGH CONFIDENCE.
    {{aggregated}}
```

---

## CLI Reference

```
polyflow new "description" -o f.yaml  Generate workflow from natural language
polyflow run <name|path> -i "..."     Run a workflow
polyflow run <name> --ci -i "..."     Run headlessly (CI/CD mode)
polyflow list [--tag security]        Browse built-in workflows
polyflow validate <file.yaml>         Validate a workflow file
polyflow pull <name>                  Download from community registry
polyflow init                         Configure API keys
polyflow doctor                       Check your setup
polyflow schema                       Show full YAML schema
```

---

## GitHub Actions

Add multi-model consensus to any repo in 30 seconds.

**1. Add to GitHub Secrets** (`Settings → Secrets → Actions`):

| Secret | Description |
|---|---|
| `OPENROUTER_API_KEY` | All models via [openrouter.ai](https://openrouter.ai) (recommended) |
| `ANTHROPIC_API_KEY` | Claude only |
| `GOOGLE_API_KEY` | Gemini only |
| `OPENAI_API_KEY` | GPT-4 only |

**2. Add a workflow file to `.github/workflows/`:**

| File | Trigger | What it does |
|---|---|---|
| [polyflow-code-review.yml](.github/workflows/polyflow-code-review.yml) | Pull request | Multi-model review posted as PR comment |
| [polyflow-security-audit.yml](.github/workflows/polyflow-security-audit.yml) | Push to main / weekly | Consensus security audit, opens issue on critical findings |
| [polyflow-pr-description.yml](.github/workflows/polyflow-pr-description.yml) | PR opened | Auto-generates PR description from diff |

**3. Done.**

---

## Available Workflows (22 built-in)

```bash
polyflow list               # see all
polyflow list --tag security
```

| Workflow | Description |
|---|---|
| `code-review-multi-model` | Parallel review, consensus findings |
| `security-audit` | OWASP-based vulnerability analysis |
| `cross-validate` | Plan → parallel validation → synthesize |
| `bug-triage` | Severity classification + fix suggestions |
| `test-generation` | Unit test generation with coverage analysis |
| `pr-description` | Auto-generate PR descriptions from diffs |
| `feature-spec` | User story → technical specification |
| `adr-generator` | Architecture Decision Record |
| `incident-postmortem` | Structured incident analysis |
| `api-documentation` | OpenAPI documentation generation |
| `database-schema-design` | Schema design with normalization review |
| `deploy-checklist` | Pre-deployment readiness check |
| `changelog-generator` | Conventional commit → changelog |
| `dependency-audit` | Vulnerability + license analysis |
| `performance-analysis` | Bottleneck identification |
| `microservice-design` | Service boundary design |
| `data-pipeline-design` | ETL/streaming architecture |
| `technical-interview` | Interview question generation |
| `content-moderation` | Multi-model policy review |
| `api-spec-design` | REST API spec from requirements |
| `code-refactoring` | Refactoring plan with safety analysis |

---

## Models

**Stable aliases** (used in all built-in workflows):

| Alias | Model | Best for |
|---|---|---|
| `claude` | Claude Sonnet 4.6 | Analysis, writing, reasoning |
| `gemini` | Gemini 2.0 Flash | Speed, cost efficiency |
| `gpt-4` | GPT-4o | Code, structured output |

**Premium aliases** (opt-in):

| Alias | Model |
|---|---|
| `claude-opus` | Claude Opus 4.6 |
| `gpt-5` | GPT-5.4 |
| `gemini-pro` | Gemini 3.1 Pro (1M context) |

Or use any [OpenRouter model ID](https://openrouter.ai/models) directly — 290+ models available.

---

## Contributing

Workflows are plain YAML — no code required.

1. Fork the repo
2. Add your workflow to `workflows/examples/`
3. Validate: `polyflow validate your-workflow.yaml`
4. Open a PR

**The best contributions use at least two models** with aggregation — that's what makes Polyflow different from single-model tools.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
