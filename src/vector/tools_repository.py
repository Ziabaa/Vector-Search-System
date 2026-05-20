from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, Field

from weaviate.classes.config import Property, Tokenization
from weaviate.collections.classes.config import DataType

from src.vector.weaviate_repository import WeaviateRepository


class ToolModel(BaseModel):
    uuid: str | UUID = Field(default=None)
    tool_name: str
    description: str
    trigger_phrases: list[str]
    score: Optional[float] = None

    @field_validator("trigger_phrases", mode="before")
    @classmethod
    def ensure_trigger_phrases_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("uuid", mode="before")
    @classmethod
    def ensure_uuid_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class ToolRepository(WeaviateRepository[ToolModel]):
    COLLECTION = "ToolSearch"
    SEARCH_ALPHA = 0.7
    MINIMAL_SCORE = 0.7

    def __init__(self) -> None:
        super().__init__(ToolModel, self.COLLECTION)

    def search(
        self,
        query: str,
        limit: int = 3,
        **kwargs,
    ) -> list[CopilotFunctionModel]:
        return self.hybrid_search(
            query=query,
            query_properties=["trigger_phrases"],
            limit=limit,
            alpha=kwargs.get("alpha", self.SEARCH_ALPHA),
            minimal_score=kwargs.get("minimal_score", self.MINIMAL_SCORE),
        )

    def create_schema(self):
        return self.create_collection(
            list_properties=[
                Property(
                    name="tool_name",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                    tokenization=Tokenization.FIELD,
                ),

                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    skip_vectorization=False,
                    tokenization=Tokenization.WORD,
                ),
                Property(
                    name="trigger_phrases",
                    data_type=DataType.TEXT_ARRAY,
                    skip_vectorization=False,
                    tokenization=Tokenization.WORD,
                ),
            ]
        )
