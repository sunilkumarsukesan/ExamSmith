# Observability & ROI

## Must-have metrics
- Time-to-first-draft paper (P50/P95)
- Total tokens in/out per run
- Cost-per-paper estimate
- Regen rate and failure reasons
- Teacher time spent (review duration)
- Approval-without-edit rate
- Export success rate

## Tracing and monitoring
- OpenTelemetry traces for orchestrator workflows
- Optional LLM tracing/observability: LangSmith or Arize Phoenix

## Cost-per-paper model
Maintain a transparent model:

$$\text{CostPerPaper} = (T_{in} \cdot P_{in}) + (T_{out} \cdot P_{out}) + C_{retrieval} + C_{storage} + C_{format}$$

Where:
- $T_{in}, T_{out}$ are token counts
- $P_{in}, P_{out}$ are provider prices
- other terms represent infrastructure (measured, not guessed)

## Dashboards
- Phase KPI dashboards per pilot school
- Quality dashboard (faithfulness distribution, rejection categories)
- Cost dashboard (per board/standard/subject)
