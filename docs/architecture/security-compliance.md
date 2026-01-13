# Security, Privacy, and Compliance

## Core controls
- Authentication: SSO or password + MFA (pilot can start simpler)
- Authorization: RBAC (Teacher, Admin, Reviewer, Ops)
- Tenant isolation: school-level logical separation (optionally separate DBs for enterprise)
- Encryption: TLS in transit; encryption at rest for DB and object storage
- Audit logs: export actions, edits, user access, and admin changes

## Student data (Phase 3)
Student answer sheets are sensitive personal data.
- Data minimization: store only what’s needed for grading and auditing
- Retention policies: configurable (e.g., delete scans after N days)
- Compliance posture: align with local regulations and GDPR-like controls (and execute DPAs where required)

Minimum privacy-by-design requirements for Phase 3:
- Lawful basis & transparency: document purpose/processing, publish clear notices, and support consent flows if required by the deployment context
- Data classification: treat answer sheets as student records + PII; prohibit unredacted PII in logs/traces
- Access controls: strict RBAC, least privilege, and per-tenant isolation for all student artifacts
- Encryption & key management: encryption at rest + in transit; tenant-aware key management for object storage when needed
- Data residency: ability to pin storage/processing to a region when required by contract/regulation
- Data subject rights: support deletion/retention overrides and export for audit; ensure backups follow retention policy
- Vendor governance: OCR/vision providers must be approved; avoid sending unnecessary PII to third parties
- Incident readiness: auditable access logs and a breach-response process (alerts, containment, reporting)

## Prompt/data leakage prevention
- No raw student data is used for training unless explicitly enabled and permitted
- PII redaction in logs and observability traces
- Principle of least privilege for tool access
