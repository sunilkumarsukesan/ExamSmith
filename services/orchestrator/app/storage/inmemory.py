from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException

from app.models import (
    Actor,
    Blueprint,
    BlueprintSlot,
    CreateRunRequest,
    Draft,
    EventType,
    EvaluationResult,
    ExportRequest,
    ExportResponse,
    GenerationRun,
    ItemAction,
    ItemActionRequest,
    ItemStatus,
    RunEvent,
    RunItem,
    RunStatus,
)
from app.storage.repo import RunRepository


class InMemoryRunRepository(RunRepository):
    def __init__(self) -> None:
        self.runs: Dict[UUID, GenerationRun] = {}
        self.items: Dict[UUID, Dict[UUID, RunItem]] = {}
        self.events: Dict[UUID, List[RunEvent]] = {}
        self.blueprints: Dict[str, Blueprint] = {}

    def _blueprint_key(self, tenant_id: str, blueprint_id: str) -> str:
        return f"{tenant_id}:{blueprint_id}"

    async def create_blueprint(self, blueprint: Blueprint, actor: Actor) -> Blueprint:
        now = datetime.utcnow()
        blueprint.updated_at = now
        if blueprint.created_at is None:
            blueprint.created_at = now
        self.blueprints[self._blueprint_key(blueprint.tenant_id, blueprint.blueprint_id)] = blueprint
        return blueprint

    async def get_blueprint(self, tenant_id: str, blueprint_id: str) -> Blueprint:
        bp = self.blueprints.get(self._blueprint_key(tenant_id, blueprint_id))
        if bp is None:
            raise HTTPException(status_code=404, detail="blueprint not found")
        return bp

    async def list_blueprints(self, tenant_id: str) -> list[Blueprint]:
        prefix = f"{tenant_id}:"
        return [bp for k, bp in self.blueprints.items() if k.startswith(prefix)]

    def _expand_blueprint_to_slots(self, blueprint: Blueprint) -> list[BlueprintSlot]:
        slots: list[BlueprintSlot] = []
        for section in blueprint.sections:
            diff = section.difficulty_range[0]
            for _ in range(section.q_count):
                slots.append(
                    BlueprintSlot(
                        section_name=section.section_name,
                        marks=section.marks_per_q,
                        difficulty=diff,
                        taxonomy_tags=section.taxonomy_tags,
                        constraints=section.constraints,
                    )
                )
        return slots

    async def create_run(self, req: CreateRunRequest, actor: Actor) -> tuple[GenerationRun, list[RunItem]]:
        run = GenerationRun(
            tenant_id=req.tenant_id,
            blueprint_id=req.blueprint_id,
            scope=req.scope,
            mode=req.mode,
            status=RunStatus.created,
        )
        if req.config is not None:
            run.config = req.config

        self.runs[run.run_id] = run
        self.items[run.run_id] = {}
        self.events[run.run_id] = []

        await self.append_event(
            RunEvent(run_id=run.run_id, type=EventType.RUN_CREATED, actor=actor, data={"mode": run.mode})
        )

        if req.blueprint_id and req.slots:
            raise HTTPException(status_code=400, detail="Provide either blueprint_id or slots, not both")

        slots = req.slots
        if req.blueprint_id and not req.slots:
            blueprint = await self.get_blueprint(req.tenant_id, req.blueprint_id)
            slots = self._expand_blueprint_to_slots(blueprint)

        created_items: list[RunItem] = []
        for slot in slots:
            item = RunItem(run_id=run.run_id, slot=slot, status=ItemStatus.planned)
            self.items[run.run_id][item.item_id] = item
            created_items.append(item)

        # Keep run at `created`. Processing (stub worker or real pipeline) moves it forward.
        self.runs[run.run_id] = run
        return run, created_items

    async def get_run(self, run_id: UUID) -> GenerationRun:
        run = self.runs.get(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run not found")
        return run

    async def list_items(self, run_id: UUID) -> list[RunItem]:
        if run_id not in self.items:
            raise HTTPException(status_code=404, detail="run not found")
        return list(self.items[run_id].values())

    async def get_item(self, run_id: UUID, item_id: UUID) -> RunItem:
        if run_id not in self.items:
            raise HTTPException(status_code=404, detail="run not found")
        item = self.items[run_id].get(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="item not found")
        return item

    async def apply_item_action(self, run_id: UUID, item_id: UUID, req: ItemActionRequest) -> RunItem:
        run = await self.get_run(run_id)
        item = await self.get_item(run_id, item_id)

        now = datetime.utcnow()
        if req.action == ItemAction.approve:
            item.status = ItemStatus.approved
            item.teacher_review.status = "approved"
            item.teacher_review.reviewed_at = now
            item.teacher_review.reviewer_id = req.actor.id
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_APPROVED, actor=req.actor)
            )

        elif req.action == ItemAction.edit:
            if not req.final_question_text or not req.final_answer_key:
                raise HTTPException(status_code=400, detail="final_question_text and final_answer_key are required")
            item.status = ItemStatus.edited
            item.teacher_review.status = "edited"
            item.teacher_review.final_question_text = req.final_question_text
            item.teacher_review.final_answer_key = req.final_answer_key
            item.teacher_review.reason = req.reason
            item.teacher_review.reviewed_at = now
            item.teacher_review.reviewer_id = req.actor.id
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_EDITED, actor=req.actor)
            )

        elif req.action == ItemAction.reject:
            item.status = ItemStatus.rejected
            item.teacher_review.status = "rejected"
            item.teacher_review.reason = req.reason
            item.teacher_review.reviewed_at = now
            item.teacher_review.reviewer_id = req.actor.id
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_REJECTED, actor=req.actor)
            )

        elif req.action == ItemAction.regenerate:
            # This is a stub until MCP + LLM wiring exists.
            item.status = ItemStatus.needs_regen
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_REGEN_REQUESTED, actor=req.actor)
            )
        else:
            raise HTTPException(status_code=400, detail="unknown action")

        item.updated_at = datetime.utcnow()
        self.items[run_id][item_id] = item

        # Update run gating status
        items = await self.list_items(run_id)
        if items and all(i.status in (ItemStatus.approved, ItemStatus.edited) for i in items):
            run.status = RunStatus.ready_to_export
        elif items:
            run.status = RunStatus.awaiting_review
        self.runs[run_id] = run

        return item

    async def export_run(self, run_id: UUID, req: ExportRequest) -> ExportResponse:
        run = await self.get_run(run_id)
        items = await self.list_items(run_id)

        if not items or not all(i.status in (ItemStatus.approved, ItemStatus.edited) for i in items):
            raise HTTPException(status_code=409, detail="run not ready to export")

        run.status = RunStatus.exporting
        self.runs[run_id] = run
        await self.append_event(RunEvent(run_id=run_id, type=EventType.EXPORT_STARTED, actor=req.actor))

        # Stub artifacts; real implementation calls Formatter MCP tool.
        artifacts = [
            {
                "format": fmt,
                "storage_ref": None,
                "signed_url": None,
                "sha256": None,
            }
            for fmt in req.formats
        ]

        run.status = RunStatus.completed
        run.completed_at = datetime.utcnow()
        self.runs[run_id] = run
        await self.append_event(RunEvent(run_id=run_id, type=EventType.EXPORT_COMPLETED, actor=req.actor))

        return ExportResponse(run_id=run_id, status=run.status, artifacts=artifacts)

    async def update_run_metrics(self, run_id: UUID, metrics_patch: dict, actor: Actor, data: dict) -> GenerationRun:
        run = await self.get_run(run_id)
        run.metrics = {**(run.metrics or {}), **(metrics_patch or {})}
        self.runs[run_id] = run
        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            payload["metrics_patch"] = metrics_patch
            await self.append_event(RunEvent(run_id=run_id, type=event_type, actor=actor, data=payload))
        return run

    async def set_run_status(self, run_id: UUID, status: RunStatus, actor: Actor, data: dict) -> GenerationRun:
        run = await self.get_run(run_id)
        run.status = status
        run.started_at = run.started_at or datetime.utcnow() if status != RunStatus.created else run.started_at
        run.completed_at = datetime.utcnow() if status in (RunStatus.completed, RunStatus.failed) else run.completed_at
        self.runs[run_id] = run

        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            await self.append_event(RunEvent(run_id=run_id, type=event_type, actor=actor, data=payload))
        return run

    async def set_item_status(self, run_id: UUID, item_id: UUID, status: ItemStatus, actor: Actor, data: dict) -> RunItem:
        item = await self.get_item(run_id, item_id)
        item.status = status
        item.updated_at = datetime.utcnow()
        self.items[run_id][item_id] = item

        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            await self.append_event(RunEvent(run_id=run_id, item_id=item_id, type=event_type, actor=actor, data=payload))
        return item

    async def save_item_draft(self, run_id: UUID, item_id: UUID, draft: Draft, actor: Actor, data: dict) -> RunItem:
        item = await self.get_item(run_id, item_id)
        item.draft = draft
        item.updated_at = datetime.utcnow()
        self.items[run_id][item_id] = item
        await self.append_event(RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_DRAFTED, actor=actor, data=data))
        return item

    async def save_item_evaluation(
        self, run_id: UUID, item_id: UUID, evaluation: EvaluationResult, actor: Actor, data: dict
    ) -> RunItem:
        item = await self.get_item(run_id, item_id)
        item.evaluation = evaluation
        item.updated_at = datetime.utcnow()
        self.items[run_id][item_id] = item
        await self.append_event(
            RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_EVALUATED, actor=actor, data=data)
        )
        return item

    async def append_event(self, event: RunEvent) -> None:
        if event.run_id not in self.events:
            self.events[event.run_id] = []
        self.events[event.run_id].append(event)

    async def list_events(self, run_id: UUID) -> list[RunEvent]:
        if run_id not in self.events:
            raise HTTPException(status_code=404, detail="run not found")
        return list(self.events[run_id])
