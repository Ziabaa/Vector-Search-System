from pydantic import BaseModel

from src.services.models import FoundedTool


class ExecuteRequest(BaseModel):
    query: str

