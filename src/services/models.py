from typing import Optional

from pydantic import BaseModel, Field


class FoundedTool(BaseModel):
    name: str
    params: dict = Field(
        default_factory=dict,
    )


class ProgramResponse(BaseModel):
    founded_functions: Optional[list[FoundedTool]] = Field(default_factory=list)
    answer: Optional[str] = None
