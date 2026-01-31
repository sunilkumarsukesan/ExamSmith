# ExamSmith -- Role-Based AI Examination Platform Implementation Guide

## SYSTEM ROLE

You are an expert full-stack engineer and AI systems architect. Your
task is to extend the existing ExamSmith project into a full role-based
AI examination platform with authentication, authorization, publishing
pipeline, and AI-based evaluation.

You must follow existing project conventions and folder structure.

## 1. Core Concepts & Terminology

### Roles

-   ADMIN
-   INSTRUCTOR
-   STUDENT

### Question Paper Lifecycle

-   DRAFT
-   REVISED
-   APPROVED
-   PUBLISHED (Pipeline)

Pipeline = Published & student-visible question papers.

## 2. Authentication & Authorization (MANDATORY FIRST STEP)

Implement JWT-based Authentication

Backend: - Add Auth module - Password hashing (bcrypt) - JWT token
generation - JWT middleware

JWT Payload: { userId: string, role: "ADMIN" \| "INSTRUCTOR" \|
"STUDENT" }

Middleware: - requireAuth - requireRole(\["ADMIN"\]) -
requireRole(\["INSTRUCTOR"\]) - requireRole(\["STUDENT"\])

All protected routes MUST use middleware.

## 3. User Management (ADMIN ONLY)

MongoDB Collection: users Fields: - userId - email - passwordHash -
role - status (ACTIVE \| DISABLED) - createdAt

Admin APIs: - POST /admin/create-user - GET /admin/list-users - PUT
/admin/disable-user

Only ADMIN can access these routes.

## 4. Ingestion Pipeline (ADMIN ONLY)

ADMIN can: - Upload new book - Convert to text - Trigger injection API -
Store book metadata

APIs: - POST /admin/upload-book - POST /admin/run-injection

Books Collection: - bookId - title - sourceFile - injectedAt - status

## 5. Instructor Capabilities

View Books: - GET /instructor/books

Generate Model Question Paper: - POST /instructor/generate-paper
Inputs: - bookId - examPattern - difficulty

Initial status = DRAFT

## 6. Question Paper Management

MongoDB: question_papers

Fields: - paperId - bookId - status (DRAFT \| REVISED \| APPROVED \|
PUBLISHED) - questions\[\] - answerKey\[\] - createdBy - revisedBy\[\] -
approvedAt - publishedAt

## 7. Human-in-the-Loop (Revise)

Instructor: - PUT /instructor/revise-question

Revision History: - questionId - oldText - newText - revisedAt -
revisedBy

## 8. Approval & Pipeline Publishing

Instructor: - POST /instructor/approve-paper - POST
/instructor/publish-to-pipeline

Rules: - Only APPROVED papers can be PUBLISHED - Only PUBLISHED papers
are visible to students

## 9. PDF Generation

Both Instructor & Student: - GET /papers/:paperId/download-pdf

Generate simple text-based PDF with: - Header - Questions - Options
(MCQ) - No answer keys for student

## 10. Student Capabilities

View Published Papers: - GET /student/pipeline-papers

Take Exam: - GET /student/papers/:paperId

UI: - MCQ → Radio buttons - Descriptive → Text input

## 11. Submit & Evaluate Answers

Student: - POST /student/submit-paper

MongoDB: attempts Fields: - attemptId - studentId - paperId -
answers\[\] - submittedAt

## 12. Evaluation Engine (AI + Rule Based)

MCQ: - Exact match with answerKey

Descriptive (Semantic Evaluation):

Process: 1. Embed student answer 2. Embed answer key 3. Retrieve
relevant textbook chunks 4. Compute similarity scores

Final Score: finalScore = 0.5 \* similarity(student, answerKey) + 0.5 \*
similarity(student, textbookChunks)

MongoDB: evaluations

Fields: - attemptId - mcqScore - descriptiveScore - semanticDetails -
finalScore - evaluatedAt

## 13. Security & Rules

MANDATORY: - Role-based route protection - No hardcoded secrets - Use
env variables - Validate all inputs - Log audit trail for revisions &
approvals

## 14. Folder Structure (Extend Existing)

Backend: /auth /users /admin /instructor /student /evaluation /pipeline
/pdf /middleware /models

Frontend: /auth /admin /instructor /student /shared

## 15. Non-Functional Requirements

-   Follow existing coding patterns
-   Write clean, readable code
-   Add TODO comments where external APIs are needed
-   Do NOT break existing generation & revise flows

## 16. Implementation Priority Order

1.  Auth + RBAC
2.  User Management
3.  Question Paper Status Lifecycle
4.  Instructor Approval & Publish
5.  Student Pipeline View
6.  Exam UI
7.  Evaluation Engine
8.  PDF Generation

## FINAL RULE

If any requirement is unclear: - Add TODO - Do NOT guess - Do NOT
hardcode business logic
