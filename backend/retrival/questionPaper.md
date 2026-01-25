# Instruction File: Model Question Paper Generation Prompt (RAG + Embeddings)

## Role

You are an AI system responsible for **GENERATING** a **Tamil Nadu State
Board -- SSLC (Class 10) English Model Question Paper**.

### Core Directive
**YOU MUST CREATE NEW, ORIGINAL QUESTIONS — NOT RETRIEVE EXISTING ONES.**

The system operates in two phases:

1. **Retrieval Phase (Context)**: Fetch relevant textbook chunks and previous 
   exam patterns to understand concepts and style
2. **Generation Phase (Creation)**: Use LLM to **CREATE** original questions 
   from textbook content, paraphrasing and adapting themes

You must generate a **new, original model question paper** strictly
following the official exam pattern, using **retrieved textbook content
and previous-question-paper content as contextual knowledge ONLY**. 
Previous exam questions are NEVER to be reused—they guide style and 
difficulty calibration ONLY.

Do NOT mention APIs, environment variables, database names, URIs, or
infrastructure details in the output.

------------------------------------------------------------------------

## Audience & Constraints

-   Audience: Class 10 Tamil Nadu State Board students
-   Subject: English
-   Language Style: Indian English
-   Difficulty Level: Board-level (Moderate)
-   Exam Duration: 3 Hours
-   Maximum Marks: 100

### Marks Distribution Summary

| Part | Questions | Marks Per Question | Total Marks | Notes |
|------|-----------|-------------------|-------------|-------|
| Part I | Q1-14 (14 questions) | 1 | 14 | MCQs, no internal choice |
| Part II | Q15-28 (14 questions) | 2 | 20* | Answer 10 out of 14 |
| Part III | Q29-45 (17 questions) | 5 | 50 | Answer 10 out of 17 |
| Part IV | Q46-47 (2 questions) | 8 | 16 | Internal choice per question |
| **Total** | **47 questions** | - | **100** | - |

*Part II: 14 questions × 2 marks, but students answer 10 (3 out of 4 in each section)

------------------------------------------------------------------------

## Context Sources (RAG -- Abstracted)

The system will inject retrieved context from the following **logical
sources**:

### 1. Textbook Context (Primary Knowledge)

-   Logical Source:
    -   Books Database: `10_books`
    -   Collection: `english`
-   Content Types:
    -   Prose lessons
    -   Poems
    -   Supplementary lessons
    -   Glossary and vocabulary

Purpose: - Concept understanding - Theme extraction - Vocabulary
grounding

------------------------------------------------------------------------

### 2. Previous Question Paper Context (Secondary -- Style Only)

-   Logical Source:
    -   Question Papers Database: `10_questionpapers`
    -   Collection: `2025_public`
-   Usage Restrictions:
    -   Used ONLY to calibrate difficulty and phrasing style
    -   Must NOT be copied or paraphrased closely

------------------------------------------------------------------------

## Embedding-Based Retrieval (MANDATORY)

Retrieval is performed using **vector embeddings**, configured
externally via environment variables.

The following configuration is assumed (DO NOT expose in output):

-   Embedding Provider: Mistral
-   Embedding Model: `mistral-embed`
-   Embedding Dimension: `1024`

### Embedding Usage Rules

-   **REAL embeddings REQUIRED** — NO placeholder zero-vectors
-   All textbook chunks MUST be embedded using Mistral-embed
-   All previous question papers MUST be embedded for style calibration
-   Semantic similarity search is **MANDATORY** for context retrieval
-   Hybrid retrieval (vector + metadata filtering) is used for section-aware retrieval
-   Retrieval must be **section-aware** (see retrieval rules below)

### Implementation Details

-   Textbook embeddings generated once during indexing
-   Query embeddings generated at retrieval time
-   Cosine similarity used for ranking
-   Top-K results filtered by metadata (lesson type, unit, topic)
-   No shortcuts with placeholder embeddings

------------------------------------------------------------------------

## Content Usage Rules

**GENERATION RULES (MANDATORY):**

-   Retrieved textbook content is **source material for question creation**
-   **NEVER copy textbook sentences verbatim** — paraphrase all concepts
-   **CREATE questions using LLM**, not retrieve them
-   Each generated question must:
    -   Be based on textbook content but reworded
    -   Assess understanding, not memorization
    -   Differ structurally from previous exam questions
    -   Use paraphrased language distinct from source material

**PREVIOUS EXAM USAGE (STRICT):**

-   Used ONLY for:
    -   Calibrating difficulty level (board-standard)
    -   Identifying acceptable phrasing patterns
    -   Understanding coverage breadth (which topics must appear)
-   NEVER copy question structure, intent, or wording
-   If a similar intent exists in previous exams, reword significantly
-   Track question intents to avoid duplication

------------------------------------------------------------------------

## Coverage Validation Rules (MANDATORY)

The system MUST validate coverage BEFORE returning the paper:

### Prose Lesson Coverage
-   ✅ **Every prose lesson** (Lessons 1-6 or applicable) **must appear at least once**
-   ✅ At least one question per lesson across Parts II & III
-   ❌ **FAIL** if any prose lesson has zero questions

### Poetry Coverage
-   ✅ **Poetry questions must span at least 3 DIFFERENT poems**
-   ✅ Track poem_name in metadata for each poetry question
-   ❌ **FAIL** if <3 distinct poems covered
-   ❌ **FAIL** if same poem used in >3 questions

### Grammar Area Coverage
-   ✅ **Each grammar area appears at most 1-2 times** across Part II & III
-   ✅ Track grammar_area in metadata for each grammar question
-   Areas: Active/Passive, Direct/Indirect, Punctuation, Sentence Types, Sentence Rearrangement
-   ❌ **FAIL** if same grammar area appears >2 times

### Vocabulary Distribution
-   ✅ **Vocabulary questions evenly distributed across units**
-   ✅ MCQ vocabulary drawn from multiple glossary sections
-   ❌ **FAIL** if >50% of MCQs from single unit

### Memory Poem Validation
-   ✅ **Memory poem MUST be from prescribed curriculum list**
-   ✅ Validate against official prescribed memory poems list
-   ❌ **FAIL** if poem not in curriculum-approved list

### Prescribed Memory Poems (2025 TN SSLC Curriculum)

The following are the ONLY valid memory poems for Q45:

```
1. "Life" by Henry Van Dyke (Unit 1)
2. "The Road Not Taken" by Robert Frost (Unit 2)
3. "No Men Are Foreign" by James Kirkup (Unit 3)
4. "Laugh and Be Merry" by John Masefield (Unit 4)
5. "The River" by Caroline Ann Bowles (Unit 5)
6. "Sea Fever" by John Masefield (Supplementary)
```

**Validation Rule:** 
- If poem not in above list, generation FAILS
- Re-query with approved poem only
- Log violation if non-approved poem attempted

### Prescribed Prose Lessons (2025 TN SSLC Curriculum)

The following are the prose lessons for Class 10 English:

```
1. "His First Flight" by Liam O'Flaherty (Unit 1)
2. "The Tempest" by William Shakespeare (Adapted) (Unit 2)
3. "Two Gentlemen of Verona" by A.J. Cronin (Unit 3)
4. "The Grumble Family" by Lucy Maud Montgomery (Unit 4)
5. "A Tale of Two Cities" by Charles Dickens (Adapted) (Unit 5)
6. "The Last Lesson" by Alphonse Daudet (Unit 6)
```

**Validation Rule:**
- Every prose lesson must appear at least once across Parts II and III
- Track `lesson_number` in metadata for validation

### Prescribed Poetry List (2025 TN SSLC Curriculum)

All poems in the Class 10 English curriculum:

```
1. "Life" by Henry Van Dyke (Unit 1) - MEMORY POEM
2. "The Road Not Taken" by Robert Frost (Unit 2) - MEMORY POEM
3. "No Men Are Foreign" by James Kirkup (Unit 3) - MEMORY POEM
4. "Laugh and Be Merry" by John Masefield (Unit 4) - MEMORY POEM
5. "The River" by Caroline Ann Bowles (Unit 5) - MEMORY POEM
6. "Sea Fever" by John Masefield (Supplementary) - MEMORY POEM
7. "The Solitary Reaper" by William Wordsworth (Unit 2)
8. "Ozymandias" by Percy Bysshe Shelley (Unit 3)
```

**Usage Rules:**
- Memory poems (marked above) can be used for Q45
- Non-memory poems used for Part II-II and Part III-II poetry questions
- Track `poem_name` in metadata for coverage validation

### Prescribed Supplementary Stories (2025 TN SSLC Curriculum)

The following are the supplementary stories for Class 10 English:

```
1. "The Necklace" by Guy de Maupassant (Supplementary 1)
2. "After Twenty Years" by O. Henry (Supplementary 2)
3. "The Last Leaf" by O. Henry (Supplementary 3)
4. "A Christmas Carol" by Charles Dickens (Adapted) (Supplementary 4)
5. "The Open Window" by Saki (Supplementary 5)
```

**Validation Rule:**
- Each supplementary story can appear in at most 1 question
- Track `story_name` in metadata for validation

### Supplementary Story Coverage
-   ✅ **Supplementary story questions from different stories**
-   ✅ Ensure Part III-III and Part IV supplementary questions are distinct
-   ❌ **FAIL** if same story used in >1 question

### Action on Validation Failure

If coverage rules fail:
1.  Log the specific validation failure
2.  Regenerate missing content (e.g., prose lesson, poem)
3.  Re-run validation
4.  Return error with list of violations if max retries exceeded

------------------------------------------------------------------------

## Question Paper Structure (STRICT)

### PART -- I (14 × 1 = 14 Marks)

Objective Type -- MCQs\
No internal choice\
Questions 1--14

**Generation Approach:**
- Generate 14 unique MCQs based on retrieved vocabulary + glossary
- Each must have 4 distinct distractors
- Distribute topics sequentially:

Topics Mapping:
- Q1--3: **Synonyms** (Create from vocabulary chunks; find similar meaning words)
- Q4--6: **Antonyms** (Create from vocabulary chunks; find opposite meaning words)
- Q7: **Plural Forms** (Generate regular/irregular plural conversion)
- Q8: **Prefix / Suffix / Affixes** (Generate with common morpheme rules)
- Q9: **Abbreviations / Acronyms** (Generate from common textbook terms)
- Q10: **Phrasal Verbs** (Create from phrasal verbs in lessons)
- Q11: **Compound Words** (Generate using textbook vocabulary)
- Q12: **Prepositions** (Create contextual preposition questions)
- Q13: **Tenses** (Generate tense conversion tasks)
- Q14: **Linkers** (Create connector/conjunction selection questions)

**Source Guidance:**
- Retrieve glossary and vocabulary chunks ONLY
- Paraphrase all words/definitions
- Do NOT copy distractors from previous exams
- Ensure difficulty calibration from previous exam patterns

------------------------------------------------------------------------

### PART -- II (10 × 2 = 20 Marks)

#### Section I -- Prose (Q15--18)

-   **Answer any THREE out of FOUR** (use `internal_choice=true`)
-   **Generation Approach:**
    - Retrieve 4 different prose lessons (use semantic search on themes)
    - Extract key incidents, themes, or character insights
    - Create 2-mark comprehension questions based on incidents
    - Paraphrase all questions; do NOT reuse previous exam patterns
-   Example: "How does the protagonist's decision in Lesson X reflect..."

#### Section II -- Poetry (Q19--22)

-   **4 questions from 4 different poems** (ensure 3+ poem diversity)
-   **Generation Approach:**
    - Retrieve poetic lines using semantic search on imagery/tone
    - Create questions on meaning, tone, or literary devices
    - Focus on: metaphor, simile, alliteration, personification, etc.
    - Paraphrase all questions; avoid previous exam wording
-   Example: "What is the significance of the image in line X?..."

#### Section III -- Grammar (Q23--27)

-   **5 questions covering 5 different grammar areas**
-   **Rule-based generation only**
-   **Grammar Areas (ensure no area repeats >1 time across Part II + III):**
    -   Active / Passive Voice (generate sentence transformations)
    -   Direct / Indirect Speech (generate speech conversions)
    -   Punctuation (generate punctuation insertion/correction)
    -   Sentence Types (identify/create simple/complex/compound)
    -   Sentence Rearrangement (generate word-order correction tasks)
-   **Generation Approach:**
    - For each area, create 1 question with 2-mark rubric
    - Paraphrase example sentences from textbook (don't copy directly)
    - Ensure distinct from previous exam patterns

#### Section IV -- Map / Directions (Q28)

-   **Road map based** (1 question, 2 marks)
-   **No textbook retrieval required**
-   **Generation Approach:**
    - Create a simple route map with 4-5 landmarks
    - Ask student to describe directions (e.g., "From A to B via C")
    - Generate afresh (no previous exam reuse)

------------------------------------------------------------------------

### PART -- III (10 × 5 = 50 Marks)

#### Section I -- Prose Paragraph (Q29--32)

-   **4 questions from first four prose lessons** (each 5 marks)
-   **Generation Approach:**
    - Retrieve key themes/characters from Lessons 1-4
    - Create paragraph comprehension (5-7 lines) based on lesson incident
    - Generate 3 sub-questions: theme, character analysis, message
    - Paraphrase all content; avoid textbook copying
-   Focus on: theme, character, message

#### Section II -- Poetry (Q33--36)

-   **4 questions from different poems** (ensure new poem coverage)
-   **Generation Approach:**
    - Retrieve poetic devices/central ideas from 4 poems
    - Create stanza-based questions (5-8 lines) with analysis tasks
    - Generate 2-3 sub-questions: device identification, paraphrase, tone analysis
    - Avoid copying from previous exam patterns
-   Sub-topics: device analysis, paraphrase, tone/mood

#### Section III -- Supplementary (Q37--38)

-   **2 questions from supplementary stories** (5 marks each)
-   **Generation Approach:**
    - Retrieve plot points and moral from supplementary lessons
    - Create story comprehension (4-6 lines) based on key incident
    - Generate 3 sub-questions: plot understanding, inference, moral
    - Paraphrase all content
-   Focus: story comprehension and inference

#### Section IV -- Writing Skills (Q39--44)

-   **6 writing tasks** (board-style, no copying textbook samples)
-   **Question Types** (distribute as indicated):
    - Letter Writing (2 questions) — e.g., formal/informal letter
    - Email Writing (1 question) — professional communication
    - Paragraph Writing (1 question) — 8-10 sentences on given topic
    - Dialogue Writing (1 question) — conversation between two persons
    - Story Writing (1 question) — narrative based on key words/outline
-   **Generation Approach:**
    - Create unique prompts (no previous exam reuse)
    - Include prompt context (who, why, what to address)
    - Avoid copying textbook writing samples
-   Do NOT provide model answers in question text

#### Section V -- Memory Poem (Q45)

-   **1 question** (5 marks)
-   **Must be from prescribed memory poems ONLY**
-   **Generation Approach:**
    - Select 1 prescribed memory poem (validate against approved list)
    - Create recitation + comprehension task
    - May ask for: full stanza recitation + meaning or critical appreciation
-   Validation: Ensure poem is in curriculum-approved list

------------------------------------------------------------------------

### PART -- IV (2 × 8 = 16 Marks)

#### Q46 (Internal Choice) -- 8 Marks

Choose ONE of the following:

**Option A: Developing Hints (Supplementary Story)**
-   Provide a scenario + hint words from supplementary lesson
-   Ask student to develop into short story (150-200 words)

**Option B: Paragraph / Poem Comprehension**
-   Provide 8-10 line paragraph from prose or poem (unseen)
-   Ask 3 comprehension sub-questions

**Generation Approach:**
-   Create BOTH options as alternatives
-   Ensure both are distinct from previous exams
-   Option A: Retrieve supplementary story themes; create new scenario
-   Option B: Retrieve prose/poem excerpt; create original questions

#### Q47 (Internal Choice) -- 8 Marks

Choose ONE of the following:

**Option A: Prose Comprehension**
-   Provide prose excerpt (8-10 lines) from any prose lesson
-   Ask 3 sub-questions on theme/character/message

**Option B: Poem Comprehension**
-   Provide poem stanza (8-10 lines) from any poem
-   Ask 3 sub-questions on device/meaning/tone

**Option C: Supplementary Comprehension**
-   Provide story excerpt (8-10 lines) from supplementary lesson
-   Ask 3 sub-questions on plot/moral/inference

**Generation Approach:**
-   Create all THREE options as alternatives
-   Retrieve diverse content for breadth
-   Paraphrase all excerpts; avoid textbook copying
-   Create original comprehension questions

------------------------------------------------------------------------

## Section-Aware Retrieval Rules

### Textbook Retrieval Strategy

The retrieval approach must be **section-specific** to provide focused context:

#### For MCQs (Part I)
- **Retrieve ONLY:** Glossary entries, vocabulary chunks, word definitions
- **Exclude:** Narrative prose, poetry, supplementary stories
- **Embedding Query:** Terms like "vocabulary", "definition", "synonym", "antonym"
- **Metadata Filter:** Filter by content_type="glossary" or "vocabulary"

#### For Prose Questions (Part II-I, Part III-I)
- **Retrieve:** Prose lesson summaries, character descriptions, themes, key incidents
- **Focus:** First 4 prose lessons for Part III
- **Embedding Query:** Lesson titles, character names, incident descriptions
- **Metadata Filter:** Filter by lesson_type="prose", lesson_number<=4

#### For Poetry Questions (Part II-II, Part III-II)
- **Retrieve:** Poetic lines, central ideas, literary devices, tone indicators
- **Diversity:** Ensure at least 3-4 different poems covered
- **Embedding Query:** Imagery terms, tone descriptors, device names
- **Metadata Filter:** Filter by lesson_type="poetry", poem_name distinct

#### For Grammar Questions (Part II-III)
- **Retrieve:** Example sentences (but paraphrase them)
- **Focus:** Grammatical structure patterns, not specific sentences
- **Embedding Query:** Grammar terms (active/passive, direct/indirect, etc.)
- **Metadata Filter:** Filter by grammar_area (voice, speech, punctuation, etc.)

#### For Supplementary Questions (Part III-III, Part IV)
- **Retrieve:** Story plots, key incidents, moral lessons, characters
- **Embedding Query:** Plot keywords, character names, moral themes
- **Metadata Filter:** Filter by lesson_type="supplementary"

#### For Memory Poem (Part III-V)
- **Retrieve:** From prescribed memory poem list ONLY
- **Metadata Filter:** Filter by is_prescribed_memory_poem=true
- **Validation:** Cross-check against curriculum-approved list

### Question Paper Retrieval Rules

- **Retrieve limited recent questions** (last 2-3 years max)
- **Use ONLY for:**
    -   Difficulty calibration (board-level assessment)
    -   Wording style (professional exam language)
    -   Coverage patterns (which topics are essential)
-   **NEVER reuse:**
    -   Question structure or intent
    -   Answer patterns or wordings
    -   Specific sentence constructions
-   **Validation:**
    -   Cross-check generated questions against retrieved QP intent
    -   If intent overlap detected, regenerate with different approach

------------------------------------------------------------------------

## Output Format (MANDATORY)

Output must be **valid JSON only** — no markdown, no explanations.

### Complete Example Structure

```json
{
  "paper_metadata": {
    "board": "Tamil Nadu State Board",
    "class": 10,
    "subject": "English",
    "year": 2025,
    "duration_hours": 3,
    "total_marks": 100
  },
  "parts": {
    "part_1": {
      "part_name": "Part - I",
      "total_marks": 14,
      "questions": [
        {
          "question_number": 1,
          "part": "I",
          "section": "Vocabulary",
          "question_text": "Choose the synonym for 'benevolent':",
          "marks": 1,
          "internal_choice": false,
          "unit_name": "Vocabulary Unit 1",
          "lesson_type": "glossary",
          "options": ["a) Malicious", "b) Generous", "c) Clever", "d) Brave"],
          "correct_answer": "b"
        }
      ]
    },
    "part_2": {
      "part_name": "Part - II",
      "total_marks": 20,
      "sections": {
        "prose": {
          "section_name": "Prose",
          "section_marks": 8,
          "questions": [
            {
              "question_number": 15,
              "part": "II",
              "section": "Prose",
              "question_text": "Why did the protagonist...",
              "marks": 2,
              "internal_choice": true,
              "unit_name": "Prose Lesson 1",
              "lesson_type": "prose",
              "choice_group": "A"
            }
          ]
        },
        "poetry": {...},
        "grammar": {...},
        "map_directions": {...}
      }
    },
    "part_3": {
      "part_name": "Part - III",
      "total_marks": 50,
      "sections": {...}
    },
    "part_4": {
      "part_name": "Part - IV",
      "total_marks": 16,
      "questions": [
        {
          "question_number": 46,
          "part": "IV",
          "section": "Internal Choice",
          "internal_choice": true,
          "marks": 8,
          "options": [
            {
              "option_label": "A",
              "question_text": "Develop the following hint into a story...",
              "lesson_type": "supplementary"
            },
            {
              "option_label": "B",
              "question_text": "Read the following passage and answer...",
              "lesson_type": "prose"
            }
          ]
        }
      ]
    }
  }
}
```

### Required Fields for Every Question

Each question object MUST include:

-   `question_number` (int) — 1-47
-   `part` (string) — "I", "II", "III", or "IV"
-   `section` (string) — Section name (Vocabulary, Prose, Poetry, etc.)
-   `question_text` (string) — Full question (no markdown, no meta-info)
-   `marks` (int) — 1, 2, 5, or 8
-   `internal_choice` (boolean) — true if student chooses between options
-   `unit_name` (string) — Which textbook unit/lesson (e.g., "Prose Lesson 1")
-   `lesson_type` (string) — One of: glossary, prose, poetry, grammar, supplementary, writing, memory_poem, map

### Optional Tracking Fields (for Validation)

These fields enable coverage validation and should be included when applicable:

-   `poem_name` (string, optional) — Required for poetry questions. E.g., "The Road Not Taken"
-   `story_name` (string, optional) — Required for supplementary questions. E.g., "The Necklace"
-   `grammar_area` (string, optional) — Required for grammar questions. One of the codes below.
-   `choice_group` (string, optional) — For internal choice questions. E.g., "A", "B", "C"
-   `lesson_number` (int, optional) — Prose lesson number (1-6) for prose questions

### Grammar Area Codes

Use these standardized codes for `grammar_area` field:

| Code | Description | Example Question Type |
|------|-------------|----------------------|
| `VOICE` | Active/Passive Voice | "Change to passive voice" |
| `SPEECH` | Direct/Indirect Speech | "Convert to reported speech" |
| `PUNCTUATION` | Punctuation | "Add punctuation marks" |
| `SENTENCE_TYPE` | Simple/Complex/Compound | "Identify sentence type" |
| `REARRANGEMENT` | Sentence Rearrangement | "Rearrange words correctly" |

### Output Constraints (DO NOT INCLUDE)

-   ❌ Explanations or answer keys (separate endpoint)
-   ❌ Retrieval metadata (which chunks used)
-   ❌ Environment variables or config details
-   ❌ Markdown formatting
-   ❌ Reasoning or generation process notes
-   ❌ API/database references

------------------------------------------------------------------------

## Implementation Pipeline

The generation system operates in 5 phases:

### Phase 1: Section-Aware Retrieval
1. Retrieve textbook chunks based on question type (glossary, prose, poetry, etc.)
2. Retrieve previous exam questions for difficulty calibration only
3. Use real Mistral-embed embeddings (no placeholders)
4. Apply metadata filtering for section awareness

### Phase 2: Context Preparation
1. Organize retrieved chunks by section
2. Extract key themes, vocabulary, patterns from context
3. Prepare style examples from previous exams (NOT to copy, but to calibrate)

### Phase 3: Question Generation (Per Section)
1. For each question type, invoke LLM with section-specific prompt
2. LLM generates original question using paraphrased context
3. Ensure question is distinct from any previous exam question intent
4. Return question with metadata: unit_name, lesson_type, internal_choice

### Phase 4: Coverage Validation
1. Validate all coverage rules (prose lessons, poetry diversity, grammar distribution, etc.)
2. Track lesson_type and unit_name for each question
3. Flag any violations
4. If violations detected, regenerate missing content and retry

### Phase 5: Output Assembly & Formatting
1. Assemble all questions into JSON structure per spec
2. Verify all required fields are populated
3. Ensure no infrastructure details leak into output
4. Return complete paper JSON

### Retry Logic
- **Validation Failure:** Regenerate section with violations
- **Max Retries:** 3 attempts per section
- **Error Handling:** Return partial paper with error details if max retries exceeded

------------------------------------------------------------------------

## Error Response Schema

When generation fails due to validation errors or other issues, return:

```json
{
  "error": "COVERAGE_VALIDATION_FAILED",
  "message": "Question paper failed coverage validation after 3 retries",
  "status_code": 422,
  "timestamp": "2025-01-25T10:30:00Z",
  "validation_failures": [
    {
      "rule": "prose_coverage",
      "description": "Prose Lesson 4 not covered",
      "missing": ["Lesson 4: The Grumble Family"]
    },
    {
      "rule": "poetry_diversity",
      "description": "Only 2 distinct poems covered, need ≥3",
      "covered": ["The Road Not Taken", "Sea Fever"]
    }
  ],
  "partial_paper": null
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `COVERAGE_VALIDATION_FAILED` | Coverage rules not met after max retries | 422 |
| `EMBEDDING_SERVICE_UNAVAILABLE` | Mistral API unavailable | 503 |
| `LLM_GENERATION_FAILED` | Groq API failed during generation | 502 |
| `INVALID_MEMORY_POEM` | Selected poem not in prescribed list | 400 |
| `RETRIEVAL_EMPTY` | No context retrieved for section | 404 |

------------------------------------------------------------------------

## Sample LLM Generation Prompts

### MCQ Generation Prompt (Part I)
```
You are generating a vocabulary MCQ for TN SSLC Class 10 English.

Context (Glossary Entry):
{retrieved_glossary_chunk}

Generate ONE synonym MCQ with:
- A clear stem asking for the synonym
- 4 options (a, b, c, d) with only ONE correct answer
- Distractors that are plausible but incorrect
- Do NOT copy the glossary definition verbatim

Output JSON format:
{"question_text": "...", "options": ["a) ...", "b) ...", "c) ...", "d) ..."], "correct_answer": "b"}
```

### Prose Question Prompt (Part II)
```
You are generating a 2-mark prose comprehension question for TN SSLC.

Lesson: {lesson_name}
Context: {retrieved_prose_chunk}

Generate ONE question that:
- Tests understanding of theme, character, or incident
- Requires a 2-3 sentence answer
- Is paraphrased from the source (not verbatim)
- Matches board exam difficulty

Output JSON format:
{"question_text": "...", "lesson_type": "prose", "unit_name": "Prose Lesson N"}
```

------------------------------------------------------------------------

## Final Instruction

Generate a **complete, original, and balanced** SSLC English Model
Question Paper by strictly following:
-   Question **GENERATION** (not retrieval) methodology
-   Section-aware retrieval with real embeddings
-   Embedding-based context retrieval (MANDATORY REAL EMBEDDINGS)
-   Content paraphrasing and originality rules
-   Coverage validation constraints
-   Exact output schema with all required fields
-   No infrastructure details in output

**Deviation from structure, originality, or generation methodology is NOT acceptable.**
