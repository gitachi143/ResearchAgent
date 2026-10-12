# ROI model sketch for merchandising uplift (Aug 28, 2025)

Related: [[Shopify: Observability & Personalization discussion (Jun 18, 2025)]]

Account ID: A001
Type: artifact
Title: ROI model sketch for merchandising uplift (Aug 28, 2025)
Created At: 2025-08-28T11:05:00Z
Author: Jordan Blake
Conference ID: C2025-01
Tags: roi, personalization, commerce, ab-test, uplift-modeling

Content:
Objective:
Estimate impact of ML-driven recommendations on click-through rate (CTR), conversion rate
(CVR), and average order value (AOV) for a phased rollout beginning with Men’s Accessories.
Baseline & data inputs:
- Baseline CTR: 2.1% on recommendation modules; CVR: 3.2% sitewide; AOV:
$78; traffic: 18M weekly impressions. 
- Data features: item embeddings (co-views, co-buys), user
affinities, seasonality, margin constraints, inventory health.

Intervention assumptions:
- Expected
CTR lift: +0.4–0.8 pp; CVR lift: +0.1–0.3 pp; AOV lift: +3–6% due to long-tail discovery and better
bundling. 
- Uplift concentrated in cold-start and long-tail SKUs; guardrails cap low-margin
exposure.

Experiment design:
- 50/50 geo or traffic split; sample size powered for 95% confidence
within 2 weeks. 
- Success metric hierarchy: revenue per session > AOV > CTR; include margin-
adjusted revenue.

Rollout plan:
- Phase 0 (2 weeks): offline replay + shadow scoring to validate
ranker stability. 
- Phase 1 (2–4 weeks): limited online A/B with real-time feedback; track novelty
vs. relevance. 
- Phase 2: progressive exposure to additional categories.

Risks & mitigations:
-
Cold-start for new items → hybrid ranker with business rules; 
- Inventory volatility →
availability-aware scoring; 
- Seasonal spikes → dynamic exploration rate caps.

Example back-of-
the-envelope:
If CTR increases by 0.6 pp on 18M impressions, that’s +108k clicks. With a 0.2 pp CVR
lift and AOV up 4%, estimated weekly incremental revenue ranges $280k–$520k (sensitivity attached).
Dependencies:
- Event stream (Kafka), catalog service, inventory API, consent management, security
sign-off on data flows.
