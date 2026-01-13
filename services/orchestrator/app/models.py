from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    created = "created"
    planning = "planning"
    generating = "generating"
    awaiting_review = "awaiting_review"
    ready_to_export = "ready_to_export"
    exporting = "exporting"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ItemStatus(str, Enum):
    planned = "planned"
    retrieving = "retrieving"
    retrieved = "retrieved"
    drafting = "drafting"
    drafted = "drafted"
    evaluating = "evaluating"
    needs_regen = "needs_regen"
    regenerating = "regenerating"
    needs_review = "needs_review"
    approved = "approved"
    edited = "edited"
    rejected = "rejected"
    blocked = "blocked"
    failed = "failed"


class ActorType(str, Enum):
    service = "service"
    teacher = "teacher"


class Actor(BaseModel):
    type: ActorType
    id: str


class Scope(BaseModel):
    board: str
    standard: str
    subject: str
    language: str = "en"
    chapter: Optional[str] = None
    topic: Optional[str] = None


class SlotConstraints(BaseModel):
    question_type: str = "any"  # mcq|short|long|numerical|diagram|any
    must_include_diagram: bool = False


class BlueprintSlot(BaseModel):
    slot_id: UUID = Field(default_factory=uuid4)
    section_name: str
    marks: int
    difficulty: Literal["easy", "medium", "hard"]
    taxonomy_tags: list[str] = Field(default_factory=list)
    constraints: SlotConstraints = Field(default_factory=SlotConstraints)


class BlueprintSectionTemplate(BaseModel):
    section_name: str
    q_count: int = Field(ge=1)
    marks_per_q: int = Field(ge=1)
    difficulty_range: tuple[Literal["easy", "medium", "hard"], Literal["easy", "medium", "hard"]] = (
        "easy",
        "medium",
    )
    taxonomy_tags: list[str] = Field(default_factory=list)
    constraints: SlotConstraints = Field(default_factory=SlotConstraints)


class Blueprint(BaseModel):
    blueprint_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    board: str
    standard: str
    subject: str
    total_marks: int = Field(ge=1)
    mode: Literal["strict", "free"] = "strict"
    sections: list[BlueprintSectionTemplate] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Citation(BaseModel):
    chunk_id: str
    page_start: int
    page_end: int


class Draft(BaseModel):
    question_text: str
    answer_key: str
    citations: list[Citation] = Field(default_factory=list)
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    page_refs: list[dict[str, Any]] = Field(default_factory=list)
    latex: list[str] = Field(default_factory=list)
    diagram_refs: list[str] = Field(default_factory=list)


class EvaluationScores(BaseModel):
    faithfulness: float
    relevancy: float


class EvaluationResult(BaseModel):
    scores: EvaluationScores
    passed: bool
    failures: list[str] = Field(default_factory=list)
    threshold: float = 0.85


class TeacherReview(BaseModel):
    status: Literal["needs_review", "approved", "edited", "rejected"] = "needs_review"
    final_question_text: Optional[str] = None
    final_answer_key: Optional[str] = None
    reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None


class RunItem(BaseModel):
    item_id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    slot: BlueprintSlot
    status: ItemStatus = ItemStatus.planned

    retrieval: dict[str, Any] = Field(default_factory=dict)
    draft: Optional[Draft] = None
    evaluation: Optional[EvaluationResult] = None
    teacher_review: TeacherReview = Field(default_factory=TeacherReview)

    auto_regen_attempts: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RunConfig(BaseModel):
    eval_threshold: float = 0.85
    max_auto_regen_attempts: int = 1
    max_context_tokens: int = 3500

    # LLM selection (per-run). Keep these provider/model strings flexible so
    # the Teacher Portal can choose across OpenAI/Anthropic/Azure/local/etc.
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_output_tokens: Optional[int] = None


class GenerationRun(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    blueprint_id: Optional[str] = None
    scope: Scope
    mode: Literal["strict", "free"] = "strict"

    status: RunStatus = RunStatus.created
    config: RunConfig = Field(default_factory=RunConfig)

    metrics: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EventType(str, Enum):
    RUN_CREATED = "RUN_CREATED"
    RUN_PLANNING_STARTED = "RUN_PLANNING_STARTED"
    RUN_GENERATING_STARTED = "RUN_GENERATING_STARTED"
    RUN_AWAITING_REVIEW = "RUN_AWAITING_REVIEW"
    RUN_METRICS_UPDATED = "RUN_METRICS_UPDATED"
    SCOPE_RESOLVED = "SCOPE_RESOLVED"
    ITEM_RETRIEVED = "ITEM_RETRIEVED"
    ITEM_DRAFTED = "ITEM_DRAFTED"
    ITEM_EVALUATED = "ITEM_EVALUATED"
    ITEM_REGEN_REQUESTED = "ITEM_REGEN_REQUESTED"
    ITEM_REGENERATED = "ITEM_REGENERATED"
    TEACHER_APPROVED = "TEACHER_APPROVED"
    TEACHER_EDITED = "TEACHER_EDITED"
    TEACHER_REJECTED = "TEACHER_REJECTED"
    EXPORT_STARTED = "EXPORT_STARTED"
    EXPORT_COMPLETED = "EXPORT_COMPLETED"
    RUN_FAILED = "RUN_FAILED"


class RunEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    item_id: Optional[UUID] = None
    type: EventType
    ts: datetime = Field(default_factory=datetime.utcnow)
    actor: Actor
    data: dict[str, Any] = Field(default_factory=dict)


class CreateRunRequest(BaseModel):
    tenant_id: str
    blueprint_id: Optional[str] = None
    scope: Scope
    mode: Literal["strict", "free"] = "strict"
    config: Optional[RunConfig] = None
    slots: list[BlueprintSlot] = Field(default_factory=list)


class CreateBlueprintRequest(BaseModel):
    tenant_id: str
    blueprint_id: Optional[str] = None
    board: str
    standard: str
    subject: str
    total_marks: int
    mode: Literal["strict", "free"] = "strict"
    sections: list[BlueprintSectionTemplate] = Field(default_factory=list)


class CreateBlueprintResponse(BaseModel):
    blueprint: Blueprint


class CreateRunResponse(BaseModel):
    run: GenerationRun
    items: list[RunItem]


class ItemAction(str, Enum):
    approve = "approve"
    edit = "edit"
    reject = "reject"
    regenerate = "regenerate"


class ItemActionRequest(BaseModel):
    actor: Actor
    action: ItemAction
    final_question_text: Optional[str] = None
    final_answer_key: Optional[str] = None
    reason: Optional[str] = None


class ExportRequest(BaseModel):
    actor: Actor
    formats: list[Literal["docx", "pdf"]] = Field(default_factory=lambda: ["docx"])
    template: str = "default"
    include_internal_citations: bool = True


class ExportResponse(BaseModel):
    run_id: UUID
    status: RunStatus
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
