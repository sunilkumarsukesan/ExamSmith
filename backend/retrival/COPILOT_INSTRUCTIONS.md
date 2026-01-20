# COPILOT INSTRUCTIONS --- ExamSmith Backend Plan

## Project Context

You are helping build **ExamSmith**, an AI-powered education system for
**Tamil Nadu SSLC (10th Standard) English**.

The system already has: - Textbook content injected into MongoDB -
Public exam question papers + answer keys injected into MongoDB -
Embeddings generated using **Mistral embedding API** - LLM inference via
**Groq API** - Backend framework: **FastAPI (Python)**

Your task is to design and implement the **retrieval and API layer**.

------------------------------------------------------------------------

## Databases & Collections

### Textbook Content

-   Database: `10_books`
-   Collection: `english`
-   Indexes:
    -   BM25 (Atlas Search)
    -   Vector (1024-dim)

### Question Papers

-   Database: `10_questionpapers`
-   Collection: `2025_public`
-   Indexes:
    -   Vector only (1024-dim)

------------------------------------------------------------------------

## Document Schema

### Common Fields

-   content (semantic text for embedding)
-   embedding (1024-dim vector)
-   metadata:
    -   exam, year, subject, standard
    -   part, section, topic
    -   marks, difficulty
    -   syllabus_map (unit, lesson_type, lesson_name)
    -   lang

### Question Paper Documents (extra field)

-   question:
    -   number
    -   type (mcq / short_answer / long_answer / or)
    -   choices (for MCQ)
    -   answer (option + text)

------------------------------------------------------------------------

## Core Design Rule

Store **semantic text** in `content` and **exam logic** inside
`question`. Never mix MCQ options or answers inside `content`.

------------------------------------------------------------------------

## Retrieval Modes (MANDATORY)

Implement a unified retriever with these modes:

-   concept_explanation
-   question_similarity
-   paper_generation
-   answer_evaluation

Each mode must: - Query appropriate collection(s) - Apply metadata
filters - Return normalized context blocks

------------------------------------------------------------------------

## APIs to Implement (FastAPI)

### 1. /ask

Purpose: Student doubts, explanations\
Retrieval Mode: concept_explanation\
Uses: Textbook collection (hybrid search)

### 2. /similar-questions

Purpose: Find similar public exam questions\
Retrieval Mode: question_similarity\
Uses: Question paper collection (vector search)

### 3. /generate-paper

Purpose: Generate TN SSLC model question papers\
Retrieval Mode: paper_generation\
Uses: Question paper collection + strict paper structure

### 4. /evaluate-answer

Purpose: Evaluate student answers\
Retrieval Mode: answer_evaluation\
Uses: Question paper collection (official answers)

------------------------------------------------------------------------

## Prompting Rules (Groq)

-   Use ONLY retrieved context
-   Follow TN SSLC exam structure strictly
-   Never hallucinate questions or answers
-   Prefer semantic evaluation over exact match

------------------------------------------------------------------------

## Output Expectations

-   APIs should return:
    -   LLM-generated response
    -   Source references (question number / lesson name)
-   Keep backend independent of frontend formatting

------------------------------------------------------------------------

## Final Goal

Enable: - Intelligent chatbot for students - Model question paper
generation - Automatic answer evaluation - Syllabus-aligned retrieval

This backend should be production-grade and hackathon-demo ready.
