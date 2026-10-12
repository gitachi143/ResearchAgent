# Siemens Energy: Security Q&A alignment (Sep 5, 2025)

Related: [[Siemens Energy: Turbine analytics pilot scope (Jul 19, 2025)]]

Account ID: A002
Type: security_checklist
Title: Siemens Energy: Security Q&A alignment (Sep 5, 2025)
Created At: 2025-09-05T14:20:00Z
Author: Priya Nair
Conference ID: C2025-01
Tags: security, audit, rbac, sso, iso27001, soc2

Content:
Requested controls:
- Single sign-on (SAML/OIDC), enforced MFA; fine-grained RBAC with SoD;
immutable audit logs; IP allowlists; private network egress. 
- Evidence for SOC 2 Type II; mapping
to ISO/IEC 27001:2022 Annex A; vulnerability management SLAs; incident response runbooks.

Data
flows & residency:
- Edge features computed locally; telemetry encrypted in transit (TLS 1.2+) and
at rest (CMK). 
- EU data stored in-region with logical separation; cross-region analytics limited
to anonymized aggregates.

Audit & logging:
- Append-only logs with retention ≥ 400 days; export to
customer SIEM; 
- Tamper-evidence via hash chaining; admin actions require step-up approval.
Identity & access:
- Role templates: Admin, SecOps, Maintenance Planner, Data Scientist (read-only
prod). 
- JIT elevation for sensitive operations; quarterly access reviews with downloadable
attestations.

Compliance mapping (high level):
- A.5 Information security policies → policy docs +
training cadence; 
- A.8 Asset management → inventory of gateways and certificates; 
- A.9 Access
control → SSO + RBAC; 
- A.12 Operations security → vulnerability and patch KPIs; 
- A.16 Incident
management → IR playbooks tied to CMMS tickets.

Open questions:
- Customer-managed HSM vs. provider
KMS; 
- Pen test window before production pilot; 
- Frequency of SoD attestations for contractor
accounts.
