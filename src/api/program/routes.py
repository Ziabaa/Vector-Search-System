from fastapi import APIRouter, HTTPException

from src.api.program.models import ExecuteRequest
from src.services.program import Program
from src.services.models import ProgramResponse

program_router = APIRouter(prefix="/program", tags=["program"])


@program_router.post("/execute", response_model=ProgramResponse)
async def execute_program(request: ExecuteRequest):
    try:
        result = Program().get_answer(query=request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
