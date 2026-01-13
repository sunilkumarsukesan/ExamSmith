# Question Generation

## Modes
- Strict Mode: enforce exact section counts, marks, and difficulty ranges.
- Free Mode: allocate questions by topic weightage and optional difficulty mix.

## Orchestrator pipeline (Phase 1)
1. Validate scope via Syllabus Tool
2. Build a plan from the blueprint (question slots)
3. For each slot:
   - Retrieve context pack (Retriever Tool)
   - Generate question + answer key + citations (LLM; user-selectable provider/model per run)
   - Evaluate faithfulness/relevancy (Evaluation Tool)
   - If fail and retries remain: regenerate once with failure feedback
4. Create a teacher review batch (HITL)
5. After approvals: export DOCX/PDF (Formatter Tool)

## Feedback loop (few-shot + prompt iteration)
Teacher edits/rejections are stored and used to:
- curate scope/slot-specific exemplars for few-shot prompting
- version prompt templates per subject/slot kind
- refine retrieval query templates and context-pack rules when evidence is repeatedly insufficient

## Hard constraints
- Every question must include `evidence_chunk_ids` and `page_refs`.
- Disallow out-of-scope content.
- Require structured output (JSON schema), never free-form.

## Evaluation & regeneration policy
- DeepEval checks: faithfulness and answer relevancy
- Default threshold: 0.85
- One regeneration attempt
- If second fail: deliver to teacher as “needs rewrite” with evidence shown

**Important**: a DeepEval pass is not a substitute for teacher review. Even when items pass evaluation, they still go to the Teacher Portal for approval/editing/rejection before export.

## Multimodal output handling
- If any cited chunk contains diagrams (`diagram_refs`), mark question as diagram-eligible.
- LaTeX blocks are preserved and rendered consistently in export.

## LLM selection (per run)

The Teacher Portal can select the LLM per run (tradeoff between cost and quality). The orchestrator stores the selection in `RunConfig`.

Typical config fields:
- `llm_provider`: e.g. `openai`, `azure_openai`, `anthropic`, `local`
- `llm_model`: e.g. `gpt-4o`, `gpt-4o-mini`, `claude-3-5-sonnet`, `llama-3.1-70b`
- `temperature`, `top_p`, `max_output_tokens`
