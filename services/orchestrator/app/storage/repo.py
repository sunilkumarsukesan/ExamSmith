from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.models import (
    Actor,
    Blueprint,
    CreateRunRequest,
    Draft,
    EvaluationResult,
    ExportRequest,
    ExportResponse,
    GenerationRun,
    ItemActionRequest,
    ItemStatus,
    RunEvent,
    RunItem,
    RunStatus,
)


class RunRepository(ABC):
    @abstractmethod
    async def create_blueprint(self, blueprint: Blueprint, actor: Actor) -> Blueprint:
        raise NotImplementedError

    @abstractmethod
    async def get_blueprint(self, tenant_id: str, blueprint_id: str) -> Blueprint:
        raise NotImplementedError

    @abstractmethod
    async def list_blueprints(self, tenant_id: str) -> list[Blueprint]:
        raise NotImplementedError

    @abstractmethod
    async def create_run(self, req: CreateRunRequest, actor: Actor) -> tuple[GenerationRun, list[RunItem]]:
        raise NotImplementedError

    @abstractmethod
    async def get_run(self, run_id: UUID) -> GenerationRun:
        raise NotImplementedError

    @abstractmethod
    async def list_items(self, run_id: UUID) -> list[RunItem]:
        raise NotImplementedError

    @abstractmethod
    async def get_item(self, run_id: UUID, item_id: UUID) -> RunItem:
        raise NotImplementedError

    @abstractmethod
    async def apply_item_action(self, run_id: UUID, item_id: UUID, req: ItemActionRequest) -> RunItem:
        raise NotImplementedError

    @abstractmethod
    async def export_run(self, run_id: UUID, req: ExportRequest) -> ExportResponse:
        raise NotImplementedError

    @abstractmethod
    async def update_run_metrics(self, run_id: UUID, metrics_patch: dict, actor: Actor, data: dict) -> GenerationRun:
        raise NotImplementedError

    @abstractmethod
    async def set_run_status(self, run_id: UUID, status: RunStatus, actor: Actor, data: dict) -> GenerationRun:
        raise NotImplementedError

    @abstractmethod
    async def set_item_status(
        self, run_id: UUID, item_id: UUID, status: ItemStatus, actor: Actor, data: dict
    ) -> RunItem:
        raise NotImplementedError

    @abstractmethod
    async def save_item_draft(self, run_id: UUID, item_id: UUID, draft: Draft, actor: Actor, data: dict) -> RunItem:
        raise NotImplementedError

    @abstractmethod
    async def save_item_evaluation(
        self, run_id: UUID, item_id: UUID, evaluation: EvaluationResult, actor: Actor, data: dict
    ) -> RunItem:
        raise NotImplementedError

    @abstractmethod
    async def append_event(self, event: RunEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_events(self, run_id: UUID) -> list[RunEvent]:
        raise NotImplementedError
