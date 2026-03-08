"""
Registry backed by GitHub at: polyflow-community/workflows
Workflows stored as: workflows/<name>.yaml
"""
import httpx
from pathlib import Path

REGISTRY_BASE = "https://raw.githubusercontent.com/polyflow-community/workflows/main/workflows"
REGISTRY_API = "https://api.github.com/repos/polyflow-community/workflows/contents/workflows"


async def pull_workflow(name: str, dest: Path) -> None:
    url = f"{REGISTRY_BASE}/{name}.yaml"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 404:
            raise FileNotFoundError(f"Workflow '{name}' not found in registry.")
        response.raise_for_status()
    dest.write_text(response.text)


async def list_workflows() -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(REGISTRY_API)
        response.raise_for_status()
        files = response.json()
    return [f["name"].replace(".yaml", "") for f in files if f["name"].endswith(".yaml")]
