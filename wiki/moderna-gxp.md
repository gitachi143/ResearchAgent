# Moderna: GxP analytics controls & validation (May 9, 2025)

Related: [[Mini-case: Faster site startup via CTMS integration (Aug 15, 2025)]]

Account ID: A003
Type: call_note
Title: Moderna: GxP analytics controls & validation (May 9, 2025)
Created At: 2025-05-09T17:30:00Z
Author: Alex Chen
Conference ID: None
Tags: gxp, validation, audit, vpc, cfr-part-11, lineage

Content:
Context & goals:
Clinical Ops and Data Science seek a validated analytics pathway for clinical
datasets without slowing research velocity. Attendees: Sr Director Data Science (Mei T.), GxP
Compliance Manager (Hannah O.).

Validation lifecycle (21 CFR Part 11 aligned):
- Requirements →
design specs → risk assessment → IQ/OQ/PQ → change control with traceability matrix. 
- Version-lock
all components (containers, libraries, models) with checksum verification; freeze training data
snapshots.

Controls & process:
- Immutable audit logs for every pipeline run (who/what/when/why)
and dataset lineage (source system, transformations, approvals). 
- Electronic signatures with dual-
approval for releasing validated outputs; reviewer roles separated from authors. 
- Environment
strategy: Sandbox VPC for exploration → Staging (pre-validated) → Production (validated), with gated
promotions.

Data classification & privacy:
- PHI/PII handling via tokenization; row-level access;
encrypted workspaces; activity monitoring with anomaly alerts.

KPIs & acceptance:
- Reduce time-to-
approval for analysis outputs by 30–40%; zero critical deviations; complete audit trail export < 2
minutes.

Open items:
- Clarify retention periods across studies; align e-signature ceremony with
internal SOPs; 
- Confirm Snowflake + Databricks connectivity pattern under validated constraints.
Next steps:
- Provide 21 CFR Part 11 alignment doc, sample traceability matrix, and a pilot plan for
one Phase II study in the Sandbox VPC.
