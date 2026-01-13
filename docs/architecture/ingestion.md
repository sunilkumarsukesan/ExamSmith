# Ingestion

## Goals
- Convert official textbooks (PDF) into a curriculum-aware knowledge base.
- Preserve technical accuracy for Science/Math (English-first MVP).
- Capture diagrams and LaTeX/math in a way that survives retrieval and formatting.

## Input variability (real-world)
Official PDFs may be:
- Digital-text PDFs with selectable text
- Scanned image PDFs (low resolution, skew)
- Multi-column layouts
- Watermarked/footer-heavy government PDFs

## Pipeline stages
1. PDF classification
   - Detect: digital vs scanned, columns/tables, equation-heavy pages, diagram-heavy pages.
2. Extraction
   - Text extraction (digital): pdfplumber / PyMuPDF
   - Layout detection: layoutparser (or vendor document AI)
   - OCR (scanned, printed textbooks): Tesseract baseline; cloud option for production
   - OCR (Phase 3, handwritten answer sheets): use a specialized OCR/vision service (e.g., AWS Textract or Azure AI Document Intelligence) designed for handwriting
3. Normalization
   - Remove repeated headers/footers/watermarks (book-specific templates)
   - Fix hyphenation and line-break artifacts
   - Preserve structure: headings → subheadings → paragraphs → lists
   - Store page coordinates for evidence traceability
4. Smart Chunking
   - Heading-aware chunking (ToC + detected headings)
   - Chunk sizes tuned for retrieval precision + completeness
   - Neighbor relationships stored for later expansion
5. Diagram extraction
   - Extract image regions per page
   - Store to object storage with stable IDs
   - Attach `diagram_refs[]` to chunks
6. Embeddings + indexing
   - Compute embeddings for chunk text
   - Store in MongoDB Atlas `knowledge_base`
   - Build Atlas Vector Search index on embeddings
   - Build Atlas Search (Lucene) index on `text` + metadata

## Smart Chunk schema (canonical)
Each chunk is a faithful unit of meaning and supports page-level citation.
- `chunk_id`
- `text`
- `latex[]` (normalized, optional)
- `diagram_refs[]` (optional)
- `metadata` (board, standard, subject, chapter, topic, book)
- `page_start`, `page_end` (+ optional bounding boxes)

## Quality checks (ingestion QA)
- Coverage: chapter headings detected vs expected ToC
- Text sanity: empty/garbled chunk detection
- OCR confidence thresholds (scanned)
- Duplicate detection (hash-based)

## Output
- MongoDB Atlas collection `knowledge_base`
- Object storage artifacts: extracted diagrams, optional page renders

## Phase 3 note — Scanned answer sheets (handwriting)
Handwritten OCR is a separate pipeline concern from textbook ingestion. Plan for an OCR/vision engine that can handle handwriting, plus per-field confidence scores, human verification workflows for low-confidence regions, and strict PII handling.
