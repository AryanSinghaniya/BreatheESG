# Sources and realism notes

This document describes the real-world formats considered and how sample data was shaped.

## SAP fuel and procurement
- **Format researched:** Flat report CSV exports (often SAP GUI/BI extracts) with document number, posting date, quantity, unit, amount, currency, plant, supplier, and description. Some deployments include German headers.
- **What this prototype handles:** Mixed German/English headers, inconsistent units, and basic line items for fuel or procurement.
- **Sample data:** [sample-data/sap_fuel_procurement.csv](sample-data/sap_fuel_procurement.csv) with German headers like `Belegdatum` and `Betrag` and realistic supplier names.
- **What would break:** Full IDoc/BAPI payloads, complex procurement structures, or missing document dates.

## Utility electricity
- **Format researched:** Portal CSV exports with meter id, billing period, consumption in kwh, tariff name, and site.
- **What this prototype handles:** Non-calendar billing periods and kwh usage at the meter level.
- **Sample data:** [sample-data/utility_electricity.csv](sample-data/utility_electricity.csv) includes billing start/end and tariff labels.
- **What would break:** PDF-only invoices, tiered demand charges, or reactive power fields.

## Corporate travel
- **Format researched:** Travel platform JSON exports with trip segments (origin/destination), traveler, cost, currency, and booking date. Distances can be provided or inferred from airport codes.
- **What this prototype handles:** Basic segment data with distance and unit when provided.
- **Sample data:** [sample-data/travel_export.json](sample-data/travel_export.json) includes flights, hotel, rail, and mixed currencies with one missing destination.
- **What would break:** Missing origin/destination, multi-leg itinerary merging, or strict emissions factor rules by cabin class.
