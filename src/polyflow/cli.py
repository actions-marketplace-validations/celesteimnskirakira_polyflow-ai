import asyncio
import click
from pathlib import Path
from rich.prompt import Prompt
from polyflow import __version__
from polyflow.config import Config, save_config, load_config


@click.group()
@click.version_option(__version__)
def main():
    """Polyflow — multi-model AI workflow engine."""
    pass


@main.command()
def init():
    """Configure API keys for Polyflow."""
    click.echo("Polyflow Setup — configure your API keys.\n")
    keys = {}
    for model, label in [
        ("claude", "Anthropic (Claude)"),
        ("gemini", "Google (Gemini)"),
        ("gpt-4", "OpenAI (GPT-4 / Codex)"),
    ]:
        key = Prompt.ask(f"  {label} API key (press Enter to skip)", default="")
        if key:
            keys[model] = key
    cfg = Config(api_keys=keys)
    save_config(cfg)
    click.echo("\n✓ Config saved to ~/.polyflow/config.yaml")


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True, path_type=Path))
@click.option("--input", "-i", default="", help="Input to pass to the workflow")
def run(workflow_file: Path, input: str):
    """Execute a workflow YAML file."""
    from polyflow.engine.runner import run_workflow
    if not input:
        input = click.prompt("Workflow input")
    config = load_config()
    asyncio.run(run_workflow(workflow_file, input, config))


@main.command()
@click.argument("description")
@click.option("--output", "-o", default="workflow.yaml", help="Output file path")
def new(description: str, output: str):
    """Generate a workflow YAML from a natural language description."""
    import anthropic
    config = load_config()
    api_key = config.get_api_key("claude")

    system_prompt = """You are a Polyflow workflow generator.
Convert natural language descriptions into valid Polyflow YAML workflows.
Follow the Polyflow Schema v1.0 strictly.
Output ONLY the raw YAML content, no markdown code blocks, no explanation."""

    user_prompt = f"""Generate a Polyflow workflow YAML for:
{description}

The workflow should use appropriate models (claude, gemini, gpt-4) and include
HITL checkpoints at key decision points."""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    yaml_content = response.content[0].text
    Path(output).write_text(yaml_content)
    click.echo(f"✓ Workflow saved to {output}")
    click.echo(f"\nRun it with: polyflow run {output}")
