import click
from polyflow import __version__


@click.group()
@click.version_option(__version__)
def main():
    """Polyflow — multi-model AI workflow engine."""
    pass
