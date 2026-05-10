from typing import Union

from fastapi import APIRouter, HTTPException, status

from src.api.weaviate.models import (
    AddVectorRequest,
    AddVectorsRequest,
    UpdateVectorRequest,
    VectorResponse,
    VectorsResponse,
)
from src.vector.tools_repository import ToolRepository, ToolModel
from src.utils.statuses import Status
from utils.statuses import Statuses

weaviate_router = APIRouter(prefix="/vectors", tags=["vectors"])
tool_repo = ToolRepository()


@weaviate_router.get("/", response_model=VectorsResponse)
async def get_all_vectors(
        limit: int | None = None,
        order_by: str | None = None,
):
    result = tool_repo.get_all_vectors(limit=limit, order_by=order_by)

    if isinstance(result, Status):
        if result == Statuses.not_found():
            raise HTTPException(status_code=404, detail=result.message)
        if result == Statuses.error():
            raise HTTPException(status_code=400, detail=result.message)
        raise HTTPException(status_code=500, detail=result.message)

    if result is None:
        return VectorsResponse(data=[], count=0)
    return VectorsResponse(data=result, count=len(result))


@weaviate_router.post("/", response_model=VectorsResponse, status_code=status.HTTP_201_CREATED)
async def add_vectors(request: Union[AddVectorRequest | AddVectorsRequest]):
    if isinstance(request, AddVectorRequest):
        tool = ToolModel(
            tool_name=request.tool_name,
            description=request.description,
            trigger_phrases=request.trigger_phrases,
        )
        tool_repo.insert(tool)
        return VectorsResponse(data=[tool], count=1)

    tools = [
        ToolModel(
            tool_name=v.tool_name,
            description=v.description,
            trigger_phrases=v.trigger_phrases,
        )
        for v in request.vectors
    ]

    result = tool_repo.insert_many(tools)

    if isinstance(result, Status):
        raise HTTPException(status_code=500, detail=result.message)

    return VectorsResponse(data=result, count=len(result))


@weaviate_router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vector(uuid: str):
    result = tool_repo.delete(uuid)

    if isinstance(result, Status):
        if result != Statuses.success():
            raise HTTPException(status_code=500, detail=result.message)

    return None


@weaviate_router.put("/{uuid}", response_model=VectorResponse)
async def update_vector(uuid: str, request: UpdateVectorRequest):
    existing = tool_repo.get_by_uuid(uuid)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Vector with UUID {uuid} not found")

    updated_data = existing.model_dump()
    if request.tool_name is not None:
        updated_data["tool_name"] = request.tool_name
    if request.description is not None:
        updated_data["description"] = request.description
    if request.trigger_phrases is not None:
        updated_data["trigger_phrases"] = request.trigger_phrases

    updated_tool = ToolModel(**updated_data)
    result = tool_repo.update(uuid, updated_tool)

    if isinstance(result, Status):
        raise HTTPException(status_code=500, detail=result.message)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Vector with UUID {uuid} not found")

    return VectorResponse(data=result)
