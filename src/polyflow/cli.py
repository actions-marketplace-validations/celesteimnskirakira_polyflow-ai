from __future__ import annotations
import asyncio
import sys
import click
from pathlib import Path
from rich.prompt import Prompt
from rich.console import Console
from polyflow import __version__
from polyflow.config import Config, save_config, load_config

console = Console()


@click.group()
@click.version_option(__version__)
def main():
    """Polyflow — multi-model AI workflow engine."""
    pass


@main.command()
def init():
    """Configure API keys for Polyflow."""
    click.echo("Polyflow Setup — configure your API keys.\n")

    # Check if OpenRouter key already present in env
    import os
    if os.environ.get("OPENROUTER_API_KEY"):
        click.echo("  ✓ OPENROUTER_API_KEY detected in environment (covers all models)\n")

    keys = {}
    or_key = Prompt.ask(
        "  OpenRouter API key (covers Claude + Gemini + GPT-4, press Enter to skip)",
        default="",
    )
    if or_key:
        cfg = Config(openrouter_api_key=or_key)
        save_config(cfg)
        click.echo("\n✓ Config saved to ~/.polyflow/config.yaml")
        return

    for model, label in [
        ("claude", "Anthropic (Claude)"),
        ("gemini", "Google (Gemini)"),
        ("gpt-4", "OpenAI (GPT-4)"),
    ]:
        key = Prompt.ask(f"  {label} API key (press Enter to skip)", default="")
        if key:
            keys[model] = key

    cfg = Config(api_keys=keys)
    save_config(cfg)
    click.echo("\n✓ Config saved to ~/.polyflow/config.yaml")


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True, path_type=Path))
@click.option("--input", "-i", "user_input", default="", help="Input to pass to the workflow")
@click.option("--output", "-o", default=None, help="Override save_to path for output")
def run(workflow_file: Path, user_input: str, output: str | None):
    """Execute a workflow YAML file."""
    from polyflow.engine.runner import run_workflow
    if not user_input:
        user_input = click.prompt("Workflow input")
    config = load_config()

    if not config.uses_openrouter and not config.api_keys:
        console.print(
            "[yellow]Warning: No API keys configured. "
            "Set OPENROUTER_API_KEY or run `polyflow init`.[/yellow]"
        )

    ctx = asyncio.run(run_workflow(workflow_file, user_input, config))

    if output and ctx.step_outputs:
        # Write last step output to the specified file
        last_output = list(ctx.step_outputs.values())[-1]
        Path(output).write_text(last_output, encoding="utf-8")
        console.print(f"[dim]Output written to {output}[/dim]")


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True, path_type=Path))
def validate(workflow_file: Path):
    """Validate a workflow YAML file against the schema."""
    import yaml
    from pydantic import ValidationError
    from polyflow.schema.workflow import Workflow

    try:
        raw = yaml.safe_load(workflow_file.read_text())
        wf = Workflow.model_validate(raw)
        console.print(f"[green]✓[/green] [bold]{wf.name}[/bold] — {len(wf.steps)} steps")
        for step in wf.steps:
            stype = f"[parallel, {len(step.steps)} sub-steps]" if step.type == "parallel" else f"[{step.model}]"
            hitl = " [bold yellow]+hitl[/bold yellow]" if step.hitl else ""
            console.print(f"  [dim]{step.id}[/dim] {stype}{hitl}")
    except ValidationError as e:
        console.print(f"[red]✗ Validation failed:[/red] {workflow_file.name}", err=True)
        for error in e.errors():
            loc = " → ".join(str(x) for x in error["loc"])
            console.print(f"  [red]{loc}[/red]: {error['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("description")
@click.option("--output", "-o", default="workflow.yaml", help="Output file path")
def new(description: str, output: str):
    """Generate a workflow YAML from a natural language description."""
    import anthropic
    import yaml
    from pydantic import ValidationError
    from polyflow.schema.workflow import Workflow

    config = load_config()
    if config.uses_openrouter:
        # Use OpenRouter for generation
        from openai import OpenAI
        from polyflow.models.openrouter import OPENROUTER_BASE_URL
        client_or = OpenAI(api_key=config.openrouter_api_key, base_url=OPENROUTER_BASE_URL)
        response_text = client_or.chat.completions.create(
            model="anthropic/claude-sonnet-4-5",
            max_tokens=2048,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Polyflow workflow generator. "
                        "Convert natural language descriptions into valid Polyflow YAML workflows. "
                        "Output ONLY raw YAML, no markdown fences, no explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a Polyflow workflow YAML for:\n{description}\n\n"
                        "Use models: claude, gemini, gpt-4. "
                        "Include HITL checkpoints at key decision points."
                    ),
                },
            ],
        ).choices[0].message.content
    else:
        api_key = config.get_api_key("claude")
        client_ant = anthropic.Anthropic(api_key=api_key)
        response_text = client_ant.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=(
                "You are a Polyflow workflow generator. "
                "Convert natural language descriptions into valid Polyflow YAML workflows. "
                "Output ONLY raw YAML, no markdown fences, no explanation."
            ),
            messages=[{"role": "user", "content": (
                f"Generate a Polyflow workflow YAML for:\n{description}\n\n"
                "Use models: claude, gemini, gpt-4. "
                "Include HITL checkpoints at key decision points."
            )}],
        ).content[0].text

    # Strip accidental markdown fences
    yaml_content = response_text.strip()
    if yaml_content.startswith("```"):
        lines = yaml_content.splitlines()
        yaml_content = "\n".join(
            l for l in lines if not l.startswith("```")
        ).strip()

    # Validate before saving
    try:
        raw = yaml.safe_load(yaml_content)
        wf = Workflow.model_validate(raw)
        Path(output).write_text(yaml_content)
        click.echo(f"✓ Workflow '{wf.name}' saved to {output} ({len(wf.steps)} steps)")
        click.echo(f"\nRun it with: polyflow run {output}")
    except (ValidationError, Exception) as e:
        console.print(f"[red]✗ Generated YAML failed validation:[/red] {e}")
        # Save anyway with a warning so user can inspect
        Path(output).write_text(yaml_content)
        console.print(f"[yellow]Raw output saved to {output} for inspection.[/yellow]")


@main.command()
@click.argument("name")
@click.option("--output", "-o", default=None, help="Save path (default: <name>.yaml)")
def pull(name: str, output: str):
    """Pull a workflow from the community registry."""
    from polyflow.registry.client import pull_workflow
    dest = Path(output or f"{name}.yaml")
    asyncio.run(pull_workflow(name, dest))
    click.echo(f"✓ Saved to {dest}")
    click.echo(f"Validate: polyflow validate {dest}")
    click.echo(f"Run: polyflow run {dest}")


@main.command()
def search():
    """List available workflows in the community registry."""
    from polyflow.registry.client import list_workflows
    try:
        workflows = asyncio.run(list_workflows())
        console.print("Available community workflows:\n")
        for name in workflows:
            console.print(f"  • {name}")
        console.print(f"\nInstall with: polyflow pull <name>")
    except Exception as e:
        console.print(f"[red]Registry unavailable:[/red] {e}")
        console.print("Community registry is coming soon. Check: https://github.com/celesteimnskirakira/polyflow")
