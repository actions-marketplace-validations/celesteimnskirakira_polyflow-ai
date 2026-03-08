import click
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
