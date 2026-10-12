# Shopify: Observability & Personalization discussion (Jun 18, 2025)

Related: [[ROI model sketch for merchandising uplift (Aug 28, 2025)]]

Account ID: A001
Type: call_note
Title: Shopify: Observability & Personalization discussion (Jun 18, 2025)
Created At: 2025-06-18T15:40:00Z
Author: Jordan Blake
Conference ID: None
Tags: observability, alert-fatigue, security, ml, personalization, roi

Content:
Context:
Shopify's platform teams are revisiting observability to reduce alert fatigue while the
Growth org explores AI-driven merchandising. Attendees included VP Eng Platforms (Marina L.),
Security Architect (Sofia N.).

Current stack & pain points:
- Mixed cloud (GCP + AWS), Kubernetes,
Kafka, Prometheus, Grafana, homegrown alert rules. 
- Noisy alerts with low precision; teams mute
channels during oncall rotations. 
- Limited root-cause hints; SREs manually correlate metrics,
logs, and traces. 
- Security requires tighter access reviews and clearer data residency posture for
any ML features.

Proposed approach:
- Introduce ML anomaly scoring layer that consumes metrics and
key business KPIs (checkout success rate, add-to-cart, latency) with seasonality awareness and
automatic thresholding. 
- Provide guided triage: top contributing signals, recent deploy
correlation, blast-radius heuristics. 
- For merchandising, use the same telemetry backbone to
connect customer behavior to recommendation outcomes for closed-loop learning.

Data handling &
residency:
- Prefer region-bound processing (NA/EU), with per-tenant encryption and scoped service
accounts. 
- Option to deploy scoring service in Shopify VPC; export only aggregate features when
needed for cross-region benchmarking.

Success metrics:
- Reduce false-positive alerts by 50–70%
within 60 days; median MTTD ↓ by 30%; mean MTTR ↓ by 20%. 
- For personalization pilots: +0.4–0.8 pp
CTR uplift on long-tail SKUs; +3–6% AOV in targeted categories.

Risks & constraints:
- High traffic
spikes around seasonal events; models must adapt quickly. 
- Access control must integrate with
Shopify’s SSO and approval workflows.

Open questions:
- Which product areas are safe to start with
(e.g., Men’s Accessories)? 
- How will security review residency constraints for cross-region
benchmarking?

Next steps:
- Send SOC 2 summary and data-flow diagram; propose a 2-week discovery
for alert reduction; schedule ROI-focused demo.
