from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

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


class MongoRunRepository(RunRepository):
    def __init__(self, mongo_uri: str, db_name: str) -> None:
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.runs = self.db["generation_runs"]
        self.items = self.db["run_items"]
        self.events = self.db["run_events"]
        self.blueprints = self.db["blueprints"]

    async def create_blueprint(self, blueprint: Blueprint, actor: Actor) -> Blueprint:
        now = datetime.utcnow()
        blueprint.updated_at = now
        doc = blueprint.model_dump(mode="json")

        # Upsert by (tenant_id, blueprint_id)
        await self.blueprints.update_one(
            {"tenant_id": blueprint.tenant_id, "blueprint_id": blueprint.blueprint_id},
            {"$set": doc},
            upsert=True,
        )
        return blueprint

    async def get_blueprint(self, tenant_id: str, blueprint_id: str) -> Blueprint:
        doc = await self.blueprints.find_one({"tenant_id": tenant_id, "blueprint_id": blueprint_id})
        if not doc:
            raise HTTPException(status_code=404, detail="blueprint not found")
        return Blueprint.model_validate(doc)

    async def list_blueprints(self, tenant_id: str) -> list[Blueprint]:
        cursor = self.blueprints.find({"tenant_id": tenant_id}).sort("updated_at", -1)
        docs = await cursor.to_list(length=10_000)
        return [Blueprint.model_validate(d) for d in docs]

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

        await self.runs.insert_one(run.model_dump(mode="json"))
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
            created_items.append(item)

        if created_items:
            await self.items.insert_many([i.model_dump(mode="json") for i in created_items])

        # Keep run at `created`. Processing (stub worker or real pipeline) moves it forward.

        return run, created_items

    async def get_run(self, run_id: UUID) -> GenerationRun:
        doc = await self.runs.find_one({"run_id": str(run_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="run not found")
        return GenerationRun.model_validate(doc)

    async def list_items(self, run_id: UUID) -> list[RunItem]:
        cursor = self.items.find({"run_id": str(run_id)})
        docs = await cursor.to_list(length=10_000)
        return [RunItem.model_validate(d) for d in docs]

    async def get_item(self, run_id: UUID, item_id: UUID) -> RunItem:
        doc = await self.items.find_one({"run_id": str(run_id), "item_id": str(item_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="item not found")
        return RunItem.model_validate(doc)

    async def apply_item_action(self, run_id: UUID, item_id: UUID, req: ItemActionRequest) -> RunItem:
        run = await self.get_run(run_id)
        item = await self.get_item(run_id, item_id)

        now = datetime.utcnow()
        update: dict[str, Any] = {"updated_at": now}

        if req.action == ItemAction.approve:
            update["status"] = ItemStatus.approved
            update["teacher_review"] = {
                **item.teacher_review.model_dump(mode="json"),
                "status": "approved",
                "reviewed_at": now,
                "reviewer_id": req.actor.id,
            }
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_APPROVED, actor=req.actor)
            )

        elif req.action == ItemAction.edit:
            if not req.final_question_text or not req.final_answer_key:
                raise HTTPException(status_code=400, detail="final_question_text and final_answer_key are required")
            update["status"] = ItemStatus.edited
            update["teacher_review"] = {
                **item.teacher_review.model_dump(mode="json"),
                "status": "edited",
                "final_question_text": req.final_question_text,
                "final_answer_key": req.final_answer_key,
                "reason": req.reason,
                "reviewed_at": now,
                "reviewer_id": req.actor.id,
            }
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_EDITED, actor=req.actor)
            )

        elif req.action == ItemAction.reject:
            update["status"] = ItemStatus.rejected
            update["teacher_review"] = {
                **item.teacher_review.model_dump(mode="json"),
                "status": "rejected",
                "reason": req.reason,
                "reviewed_at": now,
                "reviewer_id": req.actor.id,
            }
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.TEACHER_REJECTED, actor=req.actor)
            )

        elif req.action == ItemAction.regenerate:
            update["status"] = ItemStatus.needs_regen
            await self.append_event(
                RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_REGEN_REQUESTED, actor=req.actor)
            )
        else:
            raise HTTPException(status_code=400, detail="unknown action")

        await self.items.update_one(
            {"run_id": str(run_id), "item_id": str(item_id)},
            {"$set": update},
        )

        # Update run gating status
        items = await self.list_items(run_id)
        if items and all(i.status in (ItemStatus.approved, ItemStatus.edited) for i in items):
            run_update = {"status": RunStatus.ready_to_export}
        else:
            run_update = {"status": RunStatus.awaiting_review}
        await self.runs.update_one({"run_id": str(run_id)}, {"$set": run_update})

        return await self.get_item(run_id, item_id)

    async def export_run(self, run_id: UUID, req: ExportRequest) -> ExportResponse:
        items = await self.list_items(run_id)
        if not items or not all(i.status in (ItemStatus.approved, ItemStatus.edited) for i in items):
            raise HTTPException(status_code=409, detail="run not ready to export")

        await self.runs.update_one({"run_id": str(run_id)}, {"$set": {"status": RunStatus.exporting}})
        await self.append_event(RunEvent(run_id=run_id, type=EventType.EXPORT_STARTED, actor=req.actor))

        artifacts = [
            {"format": fmt, "storage_ref": None, "signed_url": None, "sha256": None}
            for fmt in req.formats
        ]

        await self.runs.update_one(
            {"run_id": str(run_id)},
            {"$set": {"status": RunStatus.completed, "completed_at": datetime.utcnow()}},
        )
        await self.append_event(RunEvent(run_id=run_id, type=EventType.EXPORT_COMPLETED, actor=req.actor))

        return ExportResponse(run_id=run_id, status=RunStatus.completed, artifacts=artifacts)

    async def update_run_metrics(self, run_id: UUID, metrics_patch: dict, actor: Actor, data: dict) -> GenerationRun:
        # Shallow merge; store patch under metrics.<key>
        set_doc = {f"metrics.{k}": v for k, v in (metrics_patch or {}).items()}
        if set_doc:
            await self.runs.update_one({"run_id": str(run_id)}, {"$set": set_doc})

        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            payload["metrics_patch"] = metrics_patch
            await self.append_event(RunEvent(run_id=run_id, type=event_type, actor=actor, data=payload))

        return await self.get_run(run_id)

    async def set_run_status(self, run_id: UUID, status: RunStatus, actor: Actor, data: dict) -> GenerationRun:
        update: dict[str, Any] = {"status": status}
        if status != RunStatus.created:
            update.setdefault("started_at", datetime.utcnow())
        if status in (RunStatus.completed, RunStatus.failed):
            update["completed_at"] = datetime.utcnow()

        await self.runs.update_one({"run_id": str(run_id)}, {"$set": update})

        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            await self.append_event(RunEvent(run_id=run_id, type=event_type, actor=actor, data=payload))

        return await self.get_run(run_id)

    async def set_item_status(self, run_id: UUID, item_id: UUID, status: ItemStatus, actor: Actor, data: dict) -> RunItem:
        await self.items.update_one(
            {"run_id": str(run_id), "item_id": str(item_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}},
        )

        event_type = data.get("event_type")
        if event_type:
            payload = dict(data)
            payload.pop("event_type", None)
            await self.append_event(RunEvent(run_id=run_id, item_id=item_id, type=event_type, actor=actor, data=payload))

        return await self.get_item(run_id, item_id)

    async def save_item_draft(self, run_id: UUID, item_id: UUID, draft: Draft, actor: Actor, data: dict) -> RunItem:
        await self.items.update_one(
            {"run_id": str(run_id), "item_id": str(item_id)},
            {"$set": {"draft": draft.model_dump(mode="json"), "updated_at": datetime.utcnow()}},
        )
        await self.append_event(RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_DRAFTED, actor=actor, data=data))
        return await self.get_item(run_id, item_id)

    async def save_item_evaluation(
        self, run_id: UUID, item_id: UUID, evaluation: EvaluationResult, actor: Actor, data: dict
    ) -> RunItem:
        await self.items.update_one(
            {"run_id": str(run_id), "item_id": str(item_id)},
            {"$set": {"evaluation": evaluation.model_dump(mode="json"), "updated_at": datetime.utcnow()}},
        )
        await self.append_event(RunEvent(run_id=run_id, item_id=item_id, type=EventType.ITEM_EVALUATED, actor=actor, data=data))
        return await self.get_item(run_id, item_id)

    async def append_event(self, event: RunEvent) -> None:
        await self.events.insert_one(event.model_dump(mode="json"))

    async def list_events(self, run_id: UUID) -> list[RunEvent]:
        cursor = self.events.find({"run_id": str(run_id)}).sort("ts", 1)
        docs = await cursor.to_list(length=10_000)
        return [RunEvent.model_validate(d) for d in docs]
