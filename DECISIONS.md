# Decisions

This file captures ambiguous choices, what was selected, and why.

## Ingestion mode
- **Chosen:** CSV upload for SAP and utility; JSON upload for travel.
- **Why:** SAP and utilities commonly export CSV; travel platforms expose JSON exports or APIs.
- **Ask PM:** Whether API pulls are required in phase 1, and which provider to integrate first.

## SAP data format
- **Chosen:** Flat CSV export with mixed language headers.
- **Why:** Common for SAP reports and aligns with real-world Excel/CSV extracts.
- **Subset handled:** Fuel and procurement line items with document date, quantity, unit, amount, currency, plant, supplier, description.
- **Ignored:** Full IDoc/BAPI support, plant master lookups, and account-based classification.

## Utility data format
- **Chosen:** Utility portal CSV export with billing period start/end and kwh.
- **Why:** Facilities teams often download portal exports rather than API integrations.
- **Subset handled:** Meter id, billing period end date, kwh, tariff label, site.
- **Ignored:** Demand charges, tiered tariffs, and PDF parsing.

## Travel data format
- **Chosen:** JSON export similar to Concur/Navan with trip segments.
- **Why:** Travel platforms provide JSON payloads and API exports with segment origin/destination and cost.
- **Subset handled:** Flight, hotel, rail; distance and unit when provided; booking date.
- **Ignored:** Emissions factor lookup, fare class, cabin, and multi-leg itinerary stitching.

## Database
- **Chosen:** PostgreSQL.
- **Why:** More realistic for multi-tenant production workflows and Render deployment.

## Normalization choices
- **Chosen:** Simple unit normalization (kwh, liters, km) and heuristic suspicious flags.
- **Why:** Keeps prototype focused on ingestion and review while still exposing normalization logic.
- **Ask PM:** What thresholds should trigger review, and whether they differ by client.

## Review workflow
- **Chosen:** Binary approve/reject with optional note, plus audit log on edits.
- **Why:** Minimal reviewer flow that demonstrates analyst sign-off and auditability.
- **Ask PM:** Whether a dual-review or QA stage is required before audit lock.
