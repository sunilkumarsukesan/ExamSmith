from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.models import (
    Actor,
    ActorType,
    CreateRunRequest,
    CreateRunResponse,
    ExportRequest,
    ExportResponse,
    GenerationRun,
    ItemActionRequest,
    RunConfig,
    RunEvent,
    RunItem,
)
from app.storage.repo import RunRepository
from app.settings import settings
from app.wiring import get_repo
from app.workers.generation import process_run

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=CreateRunResponse)
async def create_run(
    req: CreateRunRequest,
    background_tasks: BackgroundTasks,
    repo: RunRepository = Depends(get_repo),
) -> CreateRunResponse:
    # Actor is not in the create-run request to keep it simple for MVP.
    # If you want full auditability, pass actor in request and wire it here.
    actor = Actor(type=ActorType.service, id="orchestrator")

    # Apply defaults for optional config fields (including LLM selection)
    cfg = req.config or RunConfig()
    if req.config is None:
        cfg.max_auto_regen_attempts = settings.max_auto_regen_attempts
        cfg.eval_threshold = settings.default_eval_threshold
    cfg.llm_provider = cfg.llm_provider or settings.default_llm_provider
    cfg.llm_model = cfg.llm_model or settings.default_llm_model
    cfg.temperature = settings.default_llm_temperature if cfg.temperature is None else cfg.temperature
    cfg.top_p = settings.default_llm_top_p if cfg.top_p is None else cfg.top_p
    cfg.max_output_tokens = (
        settings.default_llm_max_output_tokens if cfg.max_output_tokens is None else cfg.max_output_tokens
    )
    req = req.model_copy(update={"config": cfg})

    run, items = await repo.create_run(req, actor=actor)

    if settings.auto_process_runs and items:
        background_tasks.add_task(process_run, run.run_id, repo, actor)

    return CreateRunResponse(run=run, items=items)


@router.post("/{run_id}/process")
async def process_existing_run(
    run_id: UUID,
    background_tasks: BackgroundTasks,
    repo: RunRepository = Depends(get_repo),
) -> dict[str, str]:
    actor = Actor(type=ActorType.service, id="orchestrator")
    background_tasks.add_task(process_run, run_id, repo, actor)
    return {"status": "queued"}


@router.get("/{run_id}", response_model=GenerationRun)
async def get_run(run_id: UUID, repo: RunRepository = Depends(get_repo)) -> GenerationRun:
    return await repo.get_run(run_id)


@router.get("/{run_id}/items", response_model=list[RunItem])
async def list_items(run_id: UUID, repo: RunRepository = Depends(get_repo)) -> list[RunItem]:
    return await repo.list_items(run_id)


@router.get("/{run_id}/events", response_model=list[RunEvent])
async def list_events(run_id: UUID, repo: RunRepository = Depends(get_repo)) -> list[RunEvent]:
    return await repo.list_events(run_id)


@router.post("/{run_id}/items/{item_id}/action", response_model=RunItem)
async def item_action(
    run_id: UUID, item_id: UUID, req: ItemActionRequest, repo: RunRepository = Depends(get_repo)
) -> RunItem:
    return await repo.apply_item_action(run_id, item_id, req)


@router.post("/{run_id}/export", response_model=ExportResponse)
async def export_run(run_id: UUID, req: ExportRequest, repo: RunRepository = Depends(get_repo)) -> ExportResponse:
    return await repo.export_run(run_id, req)
