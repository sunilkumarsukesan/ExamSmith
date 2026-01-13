from __future__ import annotations

from datetime import datetime
import json
import time
from uuid import UUID

from app.models import (
    Actor,
    Draft,
    EvaluationResult,
    EvaluationScores,
    EventType,
    ItemStatus,
    RunStatus,
)
from app.llm.factory import get_llm_client
from app.llm.types import LLMMessage, LLMRequest
from app.observability import get_tracer
from app.storage.repo import RunRepository


def _coerce_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return 0


def _coerce_float(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return 0.0


def _ms_since(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0


async def process_run(run_id: UUID, repo: RunRepository, actor: Actor) -> None:
    """Stubbed run processor.

    Moves items through a deterministic lifecycle using placeholder retrieval/generation/evaluation.

    This is intentionally simple until MCP tools + LLM provider wiring is added.
    """

    tracer = get_tracer()

    run = await repo.get_run(run_id)
    llm_info = {
        "provider": run.config.llm_provider,
        "model": run.config.llm_model,
        "temperature": run.config.temperature,
        "top_p": run.config.top_p,
        "max_output_tokens": run.config.max_output_tokens,
    }

    base_metrics = run.metrics or {}
    latency_ms = dict(base_metrics.get("latency_ms") or {})
    tokens = dict(base_metrics.get("tokens") or {})
    cost_usd = dict(base_metrics.get("cost_usd") or {})
    items_metrics = dict(base_metrics.get("items") or {})

    latency_total_ms = _coerce_float(latency_ms.get("total"))
    latency_retrieval_ms = _coerce_float(latency_ms.get("retrieval"))
    latency_llm_ms = _coerce_float(latency_ms.get("llm"))
    latency_eval_ms = _coerce_float(latency_ms.get("evaluation"))

    input_tokens_total = _coerce_int(tokens.get("input"))
    output_tokens_total = _coerce_int(tokens.get("output"))
    total_tokens_total = _coerce_int(tokens.get("total"))
    cost_known = bool(cost_usd.get("known"))
    cost_total = _coerce_float(cost_usd.get("total"))

    items_total = _coerce_int(items_metrics.get("count"))

    run_span_start = time.perf_counter()
    with tracer.start_as_current_span("run.process") as span:
        span.set_attribute("run.id", str(run_id))
        span.set_attribute("tenant.id", run.tenant_id)
        if run.config.llm_provider:
            span.set_attribute("llm.provider", run.config.llm_provider)
        if run.config.llm_model:
            span.set_attribute("llm.model", run.config.llm_model)

        await repo.set_run_status(
            run_id,
            status=RunStatus.planning,
            actor=actor,
            data={"event_type": EventType.RUN_PLANNING_STARTED, "note": "planning started", "llm": llm_info},
        )
        await repo.set_run_status(
            run_id,
            status=RunStatus.generating,
            actor=actor,
            data={"event_type": EventType.RUN_GENERATING_STARTED, "note": "generating started"},
        )

        items = await repo.list_items(run_id)
        for item in items:
            with tracer.start_as_current_span("item.process") as item_span:
                item_span.set_attribute("run.id", str(run_id))
                item_span.set_attribute("item.id", str(item.item_id))
                item_span.set_attribute("slot.section", item.slot.section_name)
                item_span.set_attribute("slot.marks", item.slot.marks)
                item_span.set_attribute("slot.difficulty", item.slot.difficulty)

                # Retrieval stub
                retrieval_start = time.perf_counter()
                with tracer.start_as_current_span("item.retrieve"):
                    await repo.set_item_status(run_id, item.item_id, ItemStatus.retrieving, actor=actor, data={})
                    retrieved_chunks = [
                        {
                            "chunk_id": "stub_chunk_1",
                            "page_start": 1,
                            "page_end": 1,
                            "text": "(stub) textbook excerpt",
                        }
                    ]
                    await repo.set_item_status(
                        run_id,
                        item.item_id,
                        ItemStatus.retrieved,
                        actor=actor,
                        data={"event_type": EventType.ITEM_RETRIEVED, "retrieved": {"chunk_ids": ["stub_chunk_1"]}},
                    )
                retrieval_ms = _ms_since(retrieval_start)
                latency_retrieval_ms += retrieval_ms

                # Drafting stub
                llm_start = time.perf_counter()
                await repo.set_item_status(run_id, item.item_id, ItemStatus.drafting, actor=actor, data={})
                llm_client = get_llm_client(run.config.llm_provider or "mock")
                prompt = (
                    f"Generate 1 exam question and answer key for: section={item.slot.section_name}, "
                    f"marks={item.slot.marks}, difficulty={item.slot.difficulty}, taxonomy={item.slot.taxonomy_tags}.\n"
                    f"Use only the provided context. Return strict JSON with keys: question_text, answer_key.\n\n"
                    f"Context:\n- {retrieved_chunks[0]['text']}"
                )

                llm_req = LLMRequest(
                    provider=run.config.llm_provider or "mock",
                    model=run.config.llm_model or "mock",
                    temperature=run.config.temperature or 0.2,
                    top_p=run.config.top_p or 1.0,
                    max_output_tokens=run.config.max_output_tokens or 800,
                    messages=[
                        LLMMessage(role="system", content="You are an exam paper question generator."),
                        LLMMessage(role="user", content=prompt),
                    ],
                )

                with tracer.start_as_current_span("item.draft.llm") as llm_span:
                    llm_span.set_attribute("llm.provider", llm_req.provider)
                    llm_span.set_attribute("llm.model", llm_req.model)
                    llm_span.set_attribute("llm.temperature", llm_req.temperature)
                    llm_span.set_attribute("llm.top_p", llm_req.top_p)
                    llm_span.set_attribute("llm.max_output_tokens", llm_req.max_output_tokens)

                    llm_resp = await llm_client.generate(llm_req)

                    if llm_resp.input_tokens is not None:
                        llm_span.set_attribute("llm.usage.input_tokens", llm_resp.input_tokens)
                    if llm_resp.output_tokens is not None:
                        llm_span.set_attribute("llm.usage.output_tokens", llm_resp.output_tokens)
                    if llm_resp.total_tokens is not None:
                        llm_span.set_attribute("llm.usage.total_tokens", llm_resp.total_tokens)
                    if llm_resp.cost_usd is not None:
                        llm_span.set_attribute("llm.cost_usd", llm_resp.cost_usd)

                llm_ms = _ms_since(llm_start)
                latency_llm_ms += llm_ms

                input_tokens_total += _coerce_int(llm_resp.input_tokens)
                output_tokens_total += _coerce_int(llm_resp.output_tokens)
                total_tokens_total += _coerce_int(llm_resp.total_tokens)
                if llm_resp.cost_usd is not None:
                    cost_known = True
                    cost_total += _coerce_float(llm_resp.cost_usd)

                q_text = ""
                answer_key = ""
                try:
                    parsed = json.loads(llm_resp.text)
                    q_text = str(parsed.get("question_text", "")).strip()
                    answer_key = str(parsed.get("answer_key", "")).strip()
                except Exception:
                    # Fallback if provider doesn't return JSON yet
                    q_text = llm_resp.text.strip()[:500]
                    answer_key = "(unparsed)"

                draft = Draft(
                    question_text=q_text,
                    answer_key=answer_key,
                    citations=[{"chunk_id": "stub_chunk_1", "page_start": 1, "page_end": 1}],  # type: ignore[arg-type]
                    evidence_chunk_ids=["stub_chunk_1"],
                    page_refs=[{"page": 1, "chunk_id": "stub_chunk_1"}],
                    latex=[],
                    diagram_refs=[],
                )
                await repo.set_item_status(run_id, item.item_id, ItemStatus.drafted, actor=actor, data={})
                await repo.save_item_draft(
                    run_id,
                    item.item_id,
                    draft=draft,
                    actor=actor,
                    data={
                        "retrieved_chunks": retrieved_chunks,
                        "llm": {
                            "provider": llm_req.provider,
                            "model": llm_req.model,
                            "temperature": llm_req.temperature,
                            "top_p": llm_req.top_p,
                            "max_output_tokens": llm_req.max_output_tokens,
                            "usage": {
                                "input_tokens": llm_resp.input_tokens,
                                "output_tokens": llm_resp.output_tokens,
                                "total_tokens": llm_resp.total_tokens,
                                "cost_usd": llm_resp.cost_usd,
                            },
                        },
                    },
                )

                # Evaluation stub
                eval_start = time.perf_counter()
                with tracer.start_as_current_span("item.evaluate"):
                    await repo.set_item_status(run_id, item.item_id, ItemStatus.evaluating, actor=actor, data={})
                    evaluation = EvaluationResult(
                        scores=EvaluationScores(faithfulness=0.90, relevancy=0.90),
                        passed=True,
                        failures=[],
                        threshold=0.85,
                    )
                    await repo.save_item_evaluation(
                        run_id,
                        item.item_id,
                        evaluation=evaluation,
                        actor=actor,
                        data={"stub": True, "ts": datetime.utcnow().isoformat()},
                    )
                eval_ms = _ms_since(eval_start)
                latency_eval_ms += eval_ms

                await repo.set_item_status(run_id, item.item_id, ItemStatus.needs_review, actor=actor, data={})

                items_total += 1

                latency_total_ms = _coerce_float(latency_total_ms)  # keep as float
                latency_total_ms = latency_retrieval_ms + latency_llm_ms + latency_eval_ms

                metrics_patch = {
                    "latency_ms": {
                        "retrieval": round(latency_retrieval_ms, 3),
                        "llm": round(latency_llm_ms, 3),
                        "evaluation": round(latency_eval_ms, 3),
                        "total": round(latency_total_ms, 3),
                    },
                    "tokens": {
                        "input": input_tokens_total,
                        "output": output_tokens_total,
                        "total": total_tokens_total,
                    },
                    "cost_usd": {"known": cost_known, "total": round(cost_total, 6) if cost_known else None},
                    "items": {"count": items_total},
                    "llm": {"provider": llm_req.provider, "model": llm_req.model},
                }

                await repo.update_run_metrics(
                    run_id,
                    metrics_patch=metrics_patch,
                    actor=actor,
                    data={
                        "event_type": EventType.RUN_METRICS_UPDATED,
                        "note": "metrics updated",
                    },
                )

        span.set_attribute("run.latency_ms.total", round(_ms_since(run_span_start), 3))
        span.set_attribute("run.items.count", items_total)
        span.set_attribute("run.tokens.input", input_tokens_total)
        span.set_attribute("run.tokens.output", output_tokens_total)
        span.set_attribute("run.tokens.total", total_tokens_total)
        if cost_known:
            span.set_attribute("run.cost_usd.total", round(cost_total, 6))

        await repo.set_run_status(
            run_id,
            status=RunStatus.awaiting_review,
            actor=actor,
            data={"event_type": EventType.RUN_AWAITING_REVIEW, "note": "awaiting teacher review"},
        )
