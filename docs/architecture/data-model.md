# Data Model

MongoDB Atlas is the primary database for vectors, metadata, blueprints, question bank, generation runs, and feedback.

## Collections

## `knowledge_base`
```json
{
  "chunk_id": "...",
  "text": "...",
  "latex": ["..."],
  "diagram_refs": ["s3://.../img.png"],
  "vector_embedding": [0.0123, ...],
  "language": "en",
  "metadata": {
    "board": "TN|CBSE",
    "standard": "X",
    "subject": "Science",
    "chapter": "...",
    "topic": "...",
    "book": "...",
    "page_start": 12,
    "page_end": 12
  }
}
```

Indexes:
- Atlas Vector Search on `vector_embedding`
- Atlas Search on `text` + filterable metadata

## `blueprints`
```json
{
  "blueprint_id": "...",
  "board": "TN|CBSE",
  "standard": "X",
  "subject": "Science",
  "total_marks": 80,
  "mode": "strict|free",
  "sections": [
    {
      "section_name": "A",
      "q_count": 14,
      "marks_per_q": 1,
      "difficulty_range": ["easy", "medium"],
      "taxonomy_tags": ["remember", "understand"]
    }
  ]
}
```

## `question_bank`
```json
{
  "q_id": "...",
  "scope": {"board":"TN","standard":"X","subject":"Science"},
  "chapter": "...",
  "text": "...",
  "answer_key": "...",
  "marks": 2,
  "difficulty": "medium",
  "taxonomy_tags": ["apply"],
  "evidence_chunk_ids": ["c1", "c2"],
  "page_refs": [{"page": 12, "chunk_id": "c1"}],
  "eval_scores": {"faithfulness": 0.92, "relevancy": 0.90},
  "teacher_status": "approved|edited|rejected",
  "teacher_edits": {"final_text": "...", "notes": "..."}
}
```

## `generation_runs`
Tracks cost, latency, model versions, prompts, and outputs per run.

## `feedback_events`
Append-only stream of teacher actions (approve/edit/reject/regenerate) for analytics and learning.

## `exemplars` (few-shot library)
Teacher-approved Q/A pairs used as retrieval-time few-shot examples.
```json
{
  "exemplar_id": "...",
  "tenant_id": "...",
  "scope": {"board":"TN","standard":"X","subject":"Science","chapter":"...","topic":"..."},
  "slot_features": {"marks": 2, "difficulty": "medium", "taxonomy_tags": ["apply"]},
  "question_text": "...",
  "answer_key": "...",
  "evidence_chunk_ids": ["c1", "c2"],
  "source": "teacher_edited|teacher_approved",
  "created_at": "...",
  "active": true
}
```

## `prompt_templates`
Versioned prompt templates per subject/slot type.
```json
{
  "template_id": "...",
  "tenant_id": "...",
  "scope": {"board":"TN","standard":"X","subject":"Science"},
  "slot_kind": "mcq|short|long|numerical|any",
  "version": 3,
  "template": "...",
  "created_at": "...",
  "active": true
}
```

## `retrieval_policies`
Tunable retrieval/query-template settings driven by teacher feedback.
```json
{
  "policy_id": "...",
  "tenant_id": "...",
  "scope": {"board":"TN","standard":"X","subject":"Science"},
  "rrf_k": 60,
  "top_k_vector": 20,
  "top_k_keyword": 20,
  "query_templates": {"definition": "...", "numerical": "..."},
  "created_at": "...",
  "active": true
}
```
