# MCP Tool Specs (JSON Schemas)

This document defines the **contract** between the Orchestrator (MCP client) and ExamSmith tool servers (MCP servers).

Design goals:
- **Stable + versioned** tool contracts so tool servers can evolve independently.
- **Strict scope enforcement**: tools must reject requests outside curriculum scope.
- **Auditability**: every tool call is traceable via `request_id` and `run_id`.

> Note: MCP defines the transport/protocol. This doc defines the **payload schemas** ExamSmith uses inside MCP tool calls.

---

## 1) Common Conventions

### 1.1 Envelope
All tool requests and responses use a consistent envelope.

**Request envelope**
```json
{
  "request_id": "uuid",
  "run_id": "uuid",
  "tool_version": "1.0.0",
  "trace": {
    "parent_span_id": "...",
    "tenant_id": "school_123",
    "actor": {"type": "service|teacher", "id": "..."}
  },
  "payload": {}
}
```

**Response envelope**
```json
{
  "request_id": "uuid",
  "ok": true,
  "result": {},
  "error": null
}
```

**Error object**
```json
{
  "code": "SCOPE_INVALID|NOT_FOUND|VALIDATION_ERROR|RATE_LIMIT|PROVIDER_ERROR|INTERNAL",
  "message": "Human-readable error",
  "details": {}
}
```

### 1.2 Common Types

**Scope**
```json
{
  "board": "TN|CBSE",
  "standard": "X|XI|XII|...",
  "subject": "Science|Mathematics|...",
  "language": "en|ta",
  "chapter": "optional",
  "topic": "optional"
}
```

**BlueprintSlot** (one question position to fill)
```json
{
  "slot_id": "uuid",
  "section_name": "A",
  "marks": 2,
  "difficulty": "easy|medium|hard",
  "taxonomy_tags": ["remember", "understand", "apply", "analyze"],
  "constraints": {
    "question_type": "mcq|short|long|numerical|diagram|any",
    "must_include_diagram": false
  }
}
```

**KnowledgeChunk**
```json
{
  "chunk_id": "...",
  "page_start": 12,
  "page_end": 12,
  "text": "...",
  "latex": ["..."],
  "diagram_refs": ["s3://bucket/path.png"],
  "metadata": {
    "board": "TN",
    "standard": "X",
    "subject": "Science",
    "chapter": "...",
    "topic": "...",
    "book": "..."
  }
}
```

---

## 2) Syllabus Tool

### Tool name
`examsmith.syllabus.resolve_scope`

### Purpose
Validate and normalize curriculum scope and return the canonical topic/chapter mapping used across retrieval and storage.

### Request payload schema
```json
{
  "scope": {"board": "TN", "standard": "X", "subject": "Science", "language": "en"},
  "requested": {
    "chapters": ["Force and Laws of Motion"],
    "topics": ["Newton's Second Law"]
  }
}
```

### Response payload schema
```json
{
  "canonical_scope": {
    "board": "TN",
    "standard": "X",
    "subject": "Science",
    "language": "en"
  },
  "resolved": {
    "chapters": [
      {
        "chapter_id": "...",
        "chapter_name": "Force and Laws of Motion",
        "topics": [
          {"topic_id": "...", "topic_name": "Newton's Second Law"}
        ]
      }
    ]
  },
  "allowed_filters": {
    "metadata_filters": {
      "board": "TN",
      "standard": "X",
      "subject": "Science"
    }
  }
}
```

---

## 3) Retriever Tool

### Tool name
`examsmith.retriever.build_context_pack`

### Purpose
Run hybrid search (vector + keyword), combine results via RRF, then build a context pack that obeys scope and evidence rules.

### Request payload schema
```json
{
  "scope": {"board": "TN", "standard": "X", "subject": "Science", "language": "en"},
  "slot": {
    "slot_id": "uuid",
    "section_name": "A",
    "marks": 2,
    "difficulty": "medium",
    "taxonomy_tags": ["understand"],
    "constraints": {"question_type": "short", "must_include_diagram": false}
  },
  "query": {
    "semantic_query": "Explain Newton's Second Law",
    "keyword_query": "Newton's Second Law definition",
    "filters": {"chapter": "Force and Laws of Motion"}
  },
  "evidence_rules": {
    "min_evidence_chunks": 2,
    "max_chunks": 12,
    "neighbor_expansion": true
  },
  "token_budget": {
    "max_context_tokens": 3500
  }
}
```

### Response payload schema
```json
{
  "context_pack": {
    "chunks": [
      {
        "chunk_id": "...",
        "page_start": 12,
        "page_end": 12,
        "text": "...",
        "latex": [],
        "diagram_refs": []
      }
    ],
    "citations": [
      {"chunk_id": "...", "page_start": 12, "page_end": 12}
    ]
  },
  "diagnostics": {
    "retrieval": {
      "vector_top_k": 40,
      "keyword_top_k": 40,
      "rrf_k": 60,
      "final_chunk_count": 8
    },
    "deduped": true
  }
}
```

---

## 4) Diagram Tool

### Tool name
`examsmith.diagram.fetch_assets`

### Purpose
Resolve `diagram_refs` to fetchable URLs/bytes and provide metadata for formatting.

### Request payload schema
```json
{
  "diagram_refs": [
    {"ref": "s3://bucket/diagrams/img_001.png", "purpose": "insert"}
  ],
  "transform": {
    "max_width_px": 1200,
    "format": "png"
  }
}
```

### Response payload schema
```json
{
  "assets": [
    {
      "ref": "s3://bucket/diagrams/img_001.png",
      "content_type": "image/png",
      "width_px": 900,
      "height_px": 600,
      "signed_url": "https://...",
      "sha256": "..."
    }
  ]
}
```

---

## 5) Formatter Tool

### Tool name
`examsmith.formatter.render_paper`

### Purpose
Render final artifacts (DOCX/PDF) with citations, LaTeX, and diagrams.

### Request payload schema
```json
{
  "paper": {
    "title": "Class X Science — Unit Test",
    "scope": {"board": "TN", "standard": "X", "subject": "Science", "language": "en"},
    "blueprint_id": "...",
    "questions": [
      {
        "q_id": "...",
        "section_name": "A",
        "marks": 2,
        "text": "...",
        "answer_key": "...",
        "citations": [{"chunk_id": "c1", "page_start": 12, "page_end": 12}],
        "diagram_refs": ["s3://bucket/diagrams/img_001.png"],
        "latex": ["\\(F=ma\\)"]
      }
    ]
  },
  "output": {
    "formats": ["docx", "pdf"],
    "template": "default",
    "include_internal_citations": true
  }
}
```

### Response payload schema
```json
{
  "artifacts": [
    {
      "format": "docx",
      "storage_ref": "s3://bucket/exports/run_123/paper.docx",
      "signed_url": "https://...",
      "sha256": "..."
    }
  ]
}
```

---

## 6) Evaluation Tool

### Tool name
`examsmith.evaluation.score_item`

### Purpose
Run DeepEval (and any additional policies) on a generated item using its evidence context.

### Request payload schema
```json
{
  "item": {
    "q_id": "...",
    "question_text": "...",
    "answer_key": "...",
    "scope": {"board": "TN", "standard": "X", "subject": "Science", "language": "en"},
    "slot_id": "...",
    "citations": [{"chunk_id": "c1", "page_start": 12, "page_end": 12}]
  },
  "context_pack": {
    "chunks": [{"chunk_id": "c1", "page_start": 12, "page_end": 12, "text": "..."}]
  },
  "thresholds": {
    "faithfulness": 0.85,
    "relevancy": 0.85
  }
}
```

### Response payload schema
```json
{
  "scores": {
    "faithfulness": 0.92,
    "relevancy": 0.90
  },
  "pass": true,
  "failures": [],
  "diagnostics": {
    "evidence_sufficiency": "ok|weak|missing",
    "notes": "Optional evaluator notes"
  }
}
```

---

## 7) Analytics Tool

### Tool name
`examsmith.analytics.record_run_metrics`

### Purpose
Record metrics used for observability and ROI (tokens, latency, teacher time, approval rates).

### Request payload schema
```json
{
  "run_id": "uuid",
  "metrics": {
    "tokens_in": 12345,
    "tokens_out": 6789,
    "llm_cost_usd": 1.23,
    "p50_latency_ms": 1200,
    "p95_latency_ms": 4500,
    "regen_rate": 0.18,
    "approval_without_edit_rate": 0.55
  },
  "dimensions": {
    "board": "TN",
    "standard": "X",
    "subject": "Science",
    "model": "provider:model-name",
    "release": "2026-01"
  }
}
```

### Response payload schema
```json
{
  "recorded": true
}
```

---

## 8) Versioning & Compatibility

- Increment `tool_version` for backwards-incompatible schema changes.
- Orchestrator must pin tool versions per environment.
- Tool servers must validate payloads strictly and reject unknown required fields.
