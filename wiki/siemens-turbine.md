# Siemens Energy: Turbine analytics pilot scope (Jul 19, 2025)

Related: [[Siemens Energy: Security Q&A alignment (Sep 5, 2025)]]

Account ID: A002
Type: meeting_note
Title: Siemens Energy: Turbine analytics pilot scope (Jul 19, 2025)
Created At: 2025-07-19T10:00:00Z
Author: Priya Nair
Conference ID: None
Tags: predictive-maintenance, edge, azure, opc-ua, iot, cmms

Content:
Attendees & objective:
Head of Digital Grid (Lukas M.), Asset Performance Lead (Anika R.). Define a
limited-scope predictive maintenance pilot for gas turbines.

Sensors & sampling plan:
- Vibration
(x/y/z accelerometers), temperature (bearing, exhaust), pressure (inlet/outlet), rotational speed.
- Target sampling: vibration 1–5 kHz (edge FFT), others 1–10 Hz; edge windowing with offline
buffering (24–48h).

Edge & ingestion architecture:
- Ruggedized Linux gateway with OPC-UA
collector; local feature extraction (FFT peaks, kurtosis, crest factor). 
- Secure MQTT/AMQP uplink
to Azure IoT Hub; processing via Azure Functions + Data Explorer; long-term storage in ADLS Gen2;
dashboards in Power BI.

Modeling & alerting:
- Unsupervised anomaly detection (isolation
forest/autoencoder) with per-asset baselines; 
- Health score trendline and predicted time-to-
maintenance windows; 
- Alerts integrated with existing CMMS ticketing and planner workflows.
Security & compliance:
- Device identity, cert rotation, RBAC via Entra ID; audit trails on all
config changes; 
- Network segmentation, zero-trust connectivity, and customer-managed keys.

KPIs &
success criteria:
- 10–15% reduction in unexpected outages; 5–8% spare-part optimization; improved
planner efficiency measured by time-to-ticket close. 
- Pilot duration 12–16 weeks; success gates at
weeks 4, 8, and 12.

Open items:
- Confirm OPC-UA namespace compatibility across turbine
generations; 
- Validate gateways in high-temperature enclosures; 
- Determine data localization
rules for EU sites.
