from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, Query

from app.models import Actor, ActorType, Blueprint, CreateBlueprintRequest, CreateBlueprintResponse
from app.storage.repo import RunRepository
from app.wiring import get_repo

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


@router.post("", response_model=CreateBlueprintResponse)
async def create_blueprint(req: CreateBlueprintRequest, repo: RunRepository = Depends(get_repo)) -> CreateBlueprintResponse:
    actor = Actor(type=ActorType.service, id="orchestrator")
    blueprint = Blueprint(
        blueprint_id=req.blueprint_id or str(uuid4()),
        tenant_id=req.tenant_id,
        board=req.board,
        standard=req.standard,
        subject=req.subject,
        total_marks=req.total_marks,
        mode=req.mode,
        sections=req.sections,
    )
    created = await repo.create_blueprint(blueprint, actor=actor)
    return CreateBlueprintResponse(blueprint=created)


@router.get("", response_model=list[Blueprint])
async def list_blueprints(
    tenant_id: str = Query(...),
    repo: RunRepository = Depends(get_repo),
) -> list[Blueprint]:
    return await repo.list_blueprints(tenant_id)


@router.get("/{blueprint_id}", response_model=Blueprint)
async def get_blueprint(
    blueprint_id: str,
    tenant_id: str = Query(...),
    repo: RunRepository = Depends(get_repo),
) -> Blueprint:
    return await repo.get_blueprint(tenant_id, blueprint_id)
