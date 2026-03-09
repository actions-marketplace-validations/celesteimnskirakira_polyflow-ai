from __future__ import annotations
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field


class OnError(BaseModel):
    retry: int = 0
    fallback: Literal["abort", "continue", "skip"] = "abort"
    partial: Optional[Literal["continue", "abort"]] = None


class HitlConfig(BaseModel):
    message: str
    options: list[str] = Field(default=["continue", "abort"], min_length=1)
    timeout: str = "10m"
    show: Optional[Literal["diff", "summary", "raw"]] = None


class AggregateConfig(BaseModel):
    mode: Literal["summary", "diff", "vote", "raw"] = "summary"
    model: Optional[str] = None
    prompt: Optional[str] = None


class ContextConfig(BaseModel):
    inject_cwd: bool = False
    inject_files: list[str] = Field(default_factory=list)
    max_file_size: str = "50kb"


class OutputConfig(BaseModel):
    format: Literal["markdown", "json", "text"] = "markdown"
    save_to: Optional[str] = None
    include: list[str] = Field(default_factory=list)


class SubStep(BaseModel):
    """A step inside a parallel block."""
    id: str
    model: str
    prompt: str
    timeout: str = "60s"
    on_error: OnError = Field(default_factory=OnError)


class Step(BaseModel):
    id: str
    name: str = ""  # optional — defaults to id if omitted

    def model_post_init(self, __context) -> None:
        if not self.name:
            self.name = self.id
    model: Optional[str] = None
    prompt: Optional[str] = None
    type: Literal["sequential", "parallel"] = "sequential"
    steps: list[SubStep] = Field(default_factory=list)   # for parallel
    aggregate: Optional[AggregateConfig] = None
    hitl: Optional[HitlConfig] = None
    on_error: OnError = Field(default_factory=OnError)
    timeout: str = "60s"
    condition: Optional[str] = Field(None, alias="if")

    model_config = {"populate_by_name": True}


# Alias for type clarity
ParallelStep = Step


class Workflow(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    tags: list[str] = Field(default_factory=list)
    vars: dict[str, str] = Field(default_factory=dict)
    context: ContextConfig = Field(default_factory=ContextConfig)
    steps: list[Step]
    output: OutputConfig = Field(default_factory=OutputConfig)
