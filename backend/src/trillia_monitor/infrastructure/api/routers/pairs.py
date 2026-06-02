from typing import Annotated

from fastapi import APIRouter, Depends

from trillia_monitor.application.use_cases.list_pairs import ListPairsUseCase

from ..dependencies import get_list_pairs_use_case
from ..schemas import PairOut

router = APIRouter()


@router.get("", response_model=list[PairOut], summary="List monitored pairs")
async def list_pairs(
    use_case: Annotated[ListPairsUseCase, Depends(get_list_pairs_use_case)],
) -> list[PairOut]:
    pairs = await use_case.execute()
    return [PairOut(pair=str(p), base=p.base, quote=p.quote) for p in pairs]
