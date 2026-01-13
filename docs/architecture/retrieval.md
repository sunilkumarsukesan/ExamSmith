# Retrieval & Context Packing

## Goals
- Find the exact textbook definitions/laws/theorems when needed (keyword).
- Preserve conceptual relevance for broader prompts (semantic).
- Package complete evidence so the LLM never sees clipped or misleading context.

## Hybrid retrieval
Use MongoDB Atlas:
- `$vectorSearch` for semantic retrieval
- `$search` (Atlas Search/Lucene) for keyword precision
- Combine rankings via Reciprocal Rank Fusion (RRF)

### RRF
For each document ranked position $r$, score contribution is:

$$\text{RRF}(d) = \sum_{i \in \{vector,keyword\}} \frac{1}{k + r_i(d)}$$

Where $k$ is a small constant (commonly 60).

## Context Pack Builder
Build the LLM-visible context pack with strict rules.

### Steps
1. Deduplicate by `chunk_id` and near-duplicate hashes
2. Neighbor expansion
   - Include adjacent chunks if a retrieved chunk is incomplete
3. Minimum evidence rule
   - Each generated question must cite ≥ N evidence chunks (configurable)
   - Evidence must remain within blueprint scope
4. Token-budget trimming
   - Trim least-useful context first
   - Never break citation integrity
5. Diagram-aware packing
   - Attach `diagram_refs` for all included chunks

### Output
- `context_pack`: ordered list of `(chunk_id, page, text, latex, diagram_refs)`
- `citations`: structured list for formatting/export

## Retrieval tool (MCP)
The Retriever MCP tool is responsible for:
- translating blueprint slot → retrieval queries
- executing hybrid search + RRF
- returning a context pack that satisfies evidence rules

## Feedback-driven retrieval improvements
Teacher edits/rejections provide signals to tune retrieval over time:
- Update slot-specific query templates when teachers consistently correct missing definitions, wrong scope, or insufficient evidence
- Adjust RRF parameters and top-K settings per subject based on approval/edit rates
- Track evidence sufficiency (did the cited chunks actually support the final teacher-approved answer?) and bias future retrieval toward more reliable chunk patterns
