from pydantic import BaseModel

from src.vector.tools_repository import ToolModel


class VectorResponse(BaseModel):
    data: ToolModel


class VectorsResponse(BaseModel):
    data: list[ToolModel]
    count: int


class AddVectorRequest(BaseModel):
    tool_name: str
    description: str
    trigger_phrases: list[str]


class AddVectorsRequest(BaseModel):
    vectors: list[AddVectorRequest]


class UpdateVectorRequest(BaseModel):
    tool_name: str | None = None
    description: str | None = None
    trigger_phrases: list[str] | None = None


class SearchRequest(BaseModel):
    query: str
    limit: int | None = None
