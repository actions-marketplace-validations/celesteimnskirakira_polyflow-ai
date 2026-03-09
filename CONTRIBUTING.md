# Contributing to Polyflow

## The Best Contribution: A Multi-Model Workflow

The highest-value contribution is a workflow that uses **at least two models in parallel** with aggregation — that's what makes Polyflow different from any other tool.

A good workflow demonstrates one of:
- Three models checking the same thing → `aggregate.mode: vote` → consensus findings
- Two models with different perspectives → `aggregate.mode: diff` → highlights disagreements
- Parallel analysis → one model synthesizes → better output than any single model

**Steps:**
1. Fork the repository
2. Create `workflows/examples/your-workflow-name.yaml`
3. Validate: `polyflow validate workflows/examples/your-workflow-name.yaml`
4. Test with a real input and document it in your PR
5. Open a pull request

**Workflow conventions:**
- Lowercase kebab-case filenames
- Include `name`, `description`, `version`, and `tags`
- Use `{{input}}` for user-provided content
- Parallel steps should use `aggregate.mode: vote` or `diff`, not just `raw`
- Prompts should be specific, not generic

**Example tags:** `code-review`, `security`, `documentation`, `testing`, `design`, `ops`, `data`

## Reporting Bugs

Open an issue at https://github.com/celesteimnskirakira/polyflow-ai/issues

Include:
- Polyflow version: `polyflow --version`
- Setup check: `polyflow doctor`
- The workflow YAML (if applicable)
- Full error message

## Development Setup

```bash
git clone https://github.com/celesteimnskirakira/polyflow
cd polyflow
pip install -e ".[dev]"

# Unit tests — no API key needed
pytest tests/ -k "not integration"

# All tests — requires OPENROUTER_API_KEY
pytest tests/
```

## Code Style

- Python 3.11+, type hints throughout
- `from __future__ import annotations` in all modules
- Pydantic v2 for schema validation
- `asyncio` for all I/O — no blocking calls in async paths
- Rich for terminal output
- New features need tests
