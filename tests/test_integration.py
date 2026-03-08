"""
Real end-to-end integration tests using OpenRouter.
Requires OPENROUTER_API_KEY environment variable.
Skipped automatically if key is not present.
"""
import os
import pytest
import yaml
from pathlib import Path
from polyflow.config import Config, load_config
from polyflow.engine.template import TemplateContext
from polyflow.engine.executor import execute_step
from polyflow.schema.workflow import Workflow, Step, SubStep, AggregateConfig



@pytest.fixture
def or_config(tmp_path):
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        pytest.skip("OPENROUTER_API_KEY not set — skipping integration tests")
    return Config(openrouter_api_key=key, config_dir=tmp_path)


# ─── Test 1: Single model (Claude via OpenRouter) ────────────────────────────

async def test_claude_single_step(or_config):
    step = Step(id="s1", name="Hello", model="claude", prompt="Reply with exactly: POLYFLOW_OK")
    ctx = TemplateContext(input="test")
    result = await execute_step(step, ctx, or_config)
    assert result is not None
    assert "POLYFLOW_OK" in result, f"Unexpected response: {result}"


# ─── Test 2: Gemini via OpenRouter ───────────────────────────────────────────

async def test_gemini_single_step(or_config):
    step = Step(id="s1", name="Gemini", model="gemini", prompt="Reply with exactly: GEMINI_OK")
    ctx = TemplateContext(input="test")
    result = await execute_step(step, ctx, or_config)
    assert result is not None
    assert "GEMINI_OK" in result, f"Unexpected response: {result}"


# ─── Test 3: GPT-4 via OpenRouter ────────────────────────────────────────────

async def test_gpt4_single_step(or_config):
    step = Step(id="s1", name="GPT4", model="gpt-4", prompt="Reply with exactly: GPT4_OK")
    ctx = TemplateContext(input="test")
    result = await execute_step(step, ctx, or_config)
    assert result is not None
    assert "GPT4_OK" in result, f"Unexpected response: {result}"


# ─── Test 4: Template variable substitution ──────────────────────────────────

async def test_template_substitution(or_config):
    step = Step(
        id="echo",
        name="Echo",
        model="claude",
        prompt="Repeat this word exactly once: {{input}}",
    )
    ctx = TemplateContext(input="FLAMINGO")
    result = await execute_step(step, ctx, or_config)
    assert result is not None
    assert "FLAMINGO" in result, f"Input variable not reflected: {result}"


# ─── Test 5: Chained steps (output of step 1 → input of step 2) ──────────────

async def test_chained_steps(or_config):
    step1 = Step(
        id="generate",
        name="Generate",
        model="claude",
        prompt="List 3 fruits. One per line. Just the names, nothing else.",
    )
    step2 = Step(
        id="count",
        name="Count",
        model="gpt-4",
        prompt="How many items are in this list?\n{{steps.generate.output}}\n\nReply with just a single digit.",
    )
    ctx = TemplateContext(input="test")

    out1 = await execute_step(step1, ctx, or_config)
    assert out1 is not None
    ctx.step_outputs["generate"] = out1

    out2 = await execute_step(step2, ctx, or_config)
    assert out2 is not None
    assert "3" in out2, f"Expected '3' in count response: {out2}"


# ─── Test 6: Parallel execution ──────────────────────────────────────────────

async def test_parallel_execution(or_config):
    step = Step(
        id="parallel",
        name="Parallel",
        type="parallel",
        steps=[
            SubStep(id="a", model="claude", prompt="Reply with exactly: ALPHA"),
            SubStep(id="b", model="gpt-4", prompt="Reply with exactly: BETA"),
        ],
        aggregate=AggregateConfig(mode="raw"),
    )
    ctx = TemplateContext(input="test")
    result = await execute_step(step, ctx, or_config)
    assert result is not None
    assert "ALPHA" in result, f"Claude response missing: {result}"
    assert "BETA" in result, f"GPT-4 response missing: {result}"


# ─── Test 7: Conditional step skipping ───────────────────────────────────────

async def test_conditional_skip(or_config):
    step = Step(
        id="skip_me",
        name="Should Skip",
        model="claude",
        prompt="This should not run.",
        condition="{{hitl.review.choice}} == 'approve'",
    )
    ctx = TemplateContext(
        input="test",
        hitl_choices={"review": {"choice": "reject"}},
    )
    result = await execute_step(step, ctx, or_config)
    assert result is None, "Step should have been skipped"


# ─── Test 8: Full workflow via runner ────────────────────────────────────────

async def test_full_workflow_runner(or_config, tmp_path):
    workflow_yaml = """
name: integration-smoke
description: "End-to-end smoke test"
version: "1.0"
steps:
  - id: plan
    name: Generate Plan
    model: claude
    prompt: |
      List 3 steps to build a REST API. Be concise, one line per step.
      Input context: {{input}}

  - id: review
    name: Review Plan
    model: gpt-4
    prompt: |
      Review this plan and rate it 1-10. Reply format: "Rating: X/10. [one sentence reason]"
      Plan: {{steps.plan.output}}
"""
    wf_path = tmp_path / "smoke.yaml"
    wf_path.write_text(workflow_yaml)

    from polyflow.engine.runner import run_workflow
    ctx = await run_workflow(wf_path, "build a todo API with FastAPI", or_config)

    assert "plan" in ctx.step_outputs
    assert "review" in ctx.step_outputs
    assert len(ctx.step_outputs["plan"]) > 20
    assert "Rating:" in ctx.step_outputs["review"], f"Review format unexpected: {ctx.step_outputs['review']}"


# ─── Test 9: save_to output ───────────────────────────────────────────────────

async def test_save_to_output(or_config, tmp_path):
    output_file = tmp_path / "output.md"
    workflow_yaml = f"""
name: save-test
version: "1.0"
output:
  format: markdown
  save_to: "{output_file}"
steps:
  - id: write
    name: Write Something
    model: claude
    prompt: "Write one sentence about Python. Be brief."
"""
    wf_path = tmp_path / "save.yaml"
    wf_path.write_text(workflow_yaml)

    from polyflow.engine.runner import run_workflow
    await run_workflow(wf_path, "test", or_config)

    assert output_file.exists(), "Output file was not created"
    content = output_file.read_text()
    assert len(content) > 10, f"Output file is empty or too short: {content!r}"


# ─── Test 10: validate command (sync) ────────────────────────────────────────

def test_validate_valid_workflow(tmp_path):
    from click.testing import CliRunner
    from polyflow.cli import validate

    wf = tmp_path / "valid.yaml"
    wf.write_text("""
name: valid-flow
version: "1.0"
steps:
  - id: s1
    name: Step 1
    model: claude
    prompt: "Hello {{input}}"
""")
    runner = CliRunner()
    result = runner.invoke(validate, [str(wf)])
    assert result.exit_code == 0
    assert "valid-flow" in result.output


def test_validate_invalid_workflow(tmp_path):
    from click.testing import CliRunner
    from polyflow.cli import validate

    wf = tmp_path / "bad.yaml"
    wf.write_text("version: '1.0'\nsteps: []")  # missing 'name'
    runner = CliRunner()
    result = runner.invoke(validate, [str(wf)])
    assert result.exit_code != 0
