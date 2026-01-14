# Observability & ROI

## Must-have metrics
- Time-to-first-draft paper (P50/P95)
- Total tokens in/out per run
- Cost-per-approved-paper estimate (₹)
- Regen rate and failure reasons
- Teacher time spent (review duration)
- Approval-without-edit rate
- Export success rate

## ROI framing (what “success” means)
ExamSmith must be cheaper than the teacher time it saves.

Suggested ROI check (per tenant/school):
$$\text{ROI} = \frac{\text{TeacherHoursSaved} \cdot \text{HourlyRate} - \text{MonthlyPlatformCost}}{\text{MonthlyPlatformCost}}$$

Where:
- TeacherHoursSaved is derived from baseline vs observed workflow time
- MonthlyPlatformCost includes LLM + cloud + ops overhead

## ROI justification (stakeholder-ready)

### Time savings
- Baseline today (manual, 100 marks): typically ~2–4 hours per paper (drafting + blueprint match + formatting + proofreading).
- With ExamSmith: typically ~25–60 minutes of teacher touch time per approved paper (review/edit + export).
- KPI (Phase 1): ≥ 60% reduction in teacher time per approved paper.

### Consistency (reduced human error)
- Scope lock + citations reduces out-of-syllabus questions.
- Strict blueprint enforcement reduces mark-split/section mistakes.
- HITL gate ensures only teacher-approved/edited content is exported.

### Scalability (100 vs 10,000 students)
- Cost scales mainly with number of approved papers exported, not student count.
- 100 students: lower paper volume → fixed costs amortize less → higher effective ₹/approved paper.
- 10,000 students: higher volume → fixed costs amortize more → lower effective ₹/approved paper.

## Tracing and monitoring
- OpenTelemetry traces for orchestrator workflows
- Optional LLM tracing/observability: LangSmith or Arize Phoenix

## Cost-per-approved-paper model
Maintain a transparent model:

$$\text{CostPerApprovedPaper} = (T_{in} \cdot P_{in}) + (T_{out} \cdot P_{out}) + C_{retrieval} + C_{storage} + C_{format}$$

Definition:
- “Approved paper” means the export gate is satisfied (all required items are approved or edited) and an export is produced.
- Costs should be reported in INR (₹) for business decision-making, even if providers bill in USD.

Where:
- $T_{in}, T_{out}$ are token counts
- $P_{in}, P_{out}$ are provider prices
- other terms represent infrastructure (measured, not guessed)

### Cost guardrails (to protect ROI)
Define a per-tenant budget and enforce alerting when exceeded.

Examples (set during Phase 0 pilot agreement):
- Hard guardrail: P95 cost-per-approved-paper (₹) must be ≤ a tenant budget (set per school)
- Soft guardrail: average cost-per-approved-paper (₹) must be ≤ X% of willingness-to-pay per approved paper

Notes:
- Use a `known vs estimated` approach: if provider pricing is unknown, report cost as “unknown” rather than $0.
- Prefer guardrails on P95 to avoid tail-cost surprises.

## Pricing model (proposal)
Credit-based subscription (MVP-friendly):
- ₹1,000 / month = 10 credits (initial assumption)
- 1 credit is consumed only on approved + exported 100-mark papers
- Drafts are free; optionally cap free regenerations per paper

### How to compute in the product
1. Capture run-level usage: tokens in/out and phase latencies.
2. Maintain a pricing table keyed by provider+model with $P_{in}, P_{out}$.
3. Compute and persist `cost_per_approved_paper` when the run becomes exportable (and/or at export).
4. Build dashboards and alerts for budget thresholds.

Implementation note:
- The Orchestrator already persists run-level metrics (tokens/latency) and emits a metrics event; cost becomes deterministic once a pricing table is supplied.

## Dashboards
- Phase KPI dashboards per pilot school
- Quality dashboard (faithfulness distribution, rejection categories)
- Cost dashboard (per board/standard/subject)

## Delivery milestone (Phase 0)
By end of Closed Pilot:
- Baseline capture implemented (manual or UI timer): teacher “time-to-paper” without ExamSmith
- Per-run metric capture verified end-to-end (tokens/latency)
- Cost-per-approved-paper (₹) dashboard and a budget alert in place
