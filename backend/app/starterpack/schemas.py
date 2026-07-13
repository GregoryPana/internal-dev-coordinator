"""Pydantic schemas for the starter-pack generator (T7: deterministic
templates + intake form only - FR-013/FR-014/FR-016. AI tailoring, review
workflow, persistence (StarterPack table) and zip export land in T8.
"""

from pydantic import BaseModel, Field


class IntakeForm(BaseModel):
    """FR-013/FR-014: structured intake for a new project's starter pack.

    project_type/classification already live on Project and drive template
    selection directly; this form only captures what Project doesn't.
    """

    users: str = Field(min_length=1, description="Who will use this system.")
    workflow: str = Field(min_length=1, description="The core workflow being digitalised.")
    data_sensitivity: str = Field(min_length=1, description="What kind of data this handles, if any.")
    integrations: str | None = Field(default=None, description="Other systems this needs to talk to.")
    deployment_target: str = Field(min_length=1, description="Where this will run (e.g. internal VM).")
    notes: str | None = None


class GeneratedFile(BaseModel):
    path: str
    content: str


class StarterPackPreview(BaseModel):
    project_id: int
    files: list[GeneratedFile]
