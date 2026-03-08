"""Validate all YAML workflow files in workflows/examples/ against the Pydantic schema."""
import pytest
import yaml
from pathlib import Path
from polyflow.schema.workflow import Workflow

WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows" / "examples"


def get_workflow_files():
    return sorted(WORKFLOWS_DIR.glob("*.yaml"))


@pytest.mark.parametrize("path", get_workflow_files(), ids=lambda p: p.name)
def test_workflow_validates(path):
    raw = yaml.safe_load(path.read_text())
    wf = Workflow.model_validate(raw)
    assert wf.name
    assert len(wf.steps) > 0
    for step in wf.steps:
        assert step.id
        assert step.name
