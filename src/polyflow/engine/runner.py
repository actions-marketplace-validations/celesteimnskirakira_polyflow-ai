from __future__ import annotations
import yaml
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from polyflow.schema.workflow import Workflow
from polyflow.engine.template import TemplateContext
from polyflow.engine.executor import execute_step
from polyflow.engine.hitl import prompt_hitl
from polyflow.config import Config, load_config

console = Console()


async def run_workflow(workflow_path: Path, user_input: str, config: Config) -> None:
    raw = yaml.safe_load(workflow_path.read_text())
    workflow = Workflow.model_validate(raw)

    ctx = TemplateContext(input=user_input, vars=workflow.vars)

    console.print(f"\n[bold green]▶ Running:[/bold green] {workflow.name}")
    console.print(f"[dim]{workflow.description or ''}[/dim]\n")

    for step in workflow.steps:
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as p:
            task = p.add_task(f"[cyan]{step.name}[/cyan]...")
            output = await execute_step(step, ctx, config)
            p.update(task, completed=True)

        if output is None:
            console.print(f"[yellow]⏭  {step.name} skipped[/yellow]")
            continue

        console.print(f"[green]✓[/green] {step.name}")
        ctx.step_outputs[step.id] = output

        if step.hitl:
            result = prompt_hitl(
                message=step.hitl.message,
                options=step.hitl.options,
                content=output if step.hitl.show else "",
            )
            ctx.hitl_choices[step.id] = {"choice": result.choice, "note": result.note}
            if result.choice == "abort":
                console.print("[red]✗ Workflow aborted by user.[/red]")
                return

    console.print("\n[bold green]✓ Workflow complete.[/bold green]")
