# Data model

This document explains the core data model used for ingestion, normalization, review, and audit.

## Goals

- Multi-tenant isolation across all rows.
- Source-of-truth tracking from raw input to normalized record.
- Explicit Scope 1/2/3 categorization for analyst review.
- Unit normalization to enable consistent analytics.
- Audit trail for manual edits and review decisions.

## Entities

### Company
- Represents a client company.
- Every other record references a company.

### DataSource
- One per company and source type (sap, utility, travel).
- Stores ingestion config and allows multiple sources per company over time.

### IngestionBatch
- A single ingest event (file upload in this prototype).
- Tracks counts, status, and timestamps.
- Used to group all rows from a single source snapshot.

### RawRecord
- Preserves the original row payload (JSON).
- Stores row index and parsing errors without losing data.

### EmissionRecord
- Canonical row format consumed by analysts.
- Includes Scope 1/2/3, activity type, normalized units, and key dimensions.
- Links back to RawRecord and IngestionBatch.
- Status lifecycle: pending -> flagged -> approved -> locked.

### AuditLog
- Records manual edits and status changes on emission records.
- Stores previous and new values, who changed it, and why.

## Key fields

- `scope_category`: Scope 1/2/3 at the row level.
- `activity_type`: Fuel, procurement, electricity, travel.
- `activity_date`: Date used for period reporting.
- `normalized_value` and `normalized_unit`: Normalized usage units (kwh, l, km).
- `source_row_id`: Original source reference (document number, meter id, route).
- `is_suspicious`: Flag for outliers to surface in the dashboard.
- `status` + `locked_for_audit`: Review state and lock flag.

## Source-of-truth flow

1. Source data is uploaded and stored as RawRecord.
2. Normalization creates EmissionRecord with a link to RawRecord and Batch.
3. Analysts approve/flag/lock; status changes are logged in AuditLog.
4. Any edits create AuditLog entries with before/after values.

## Multi-tenancy

Every table has a foreign key to Company. Query filtering always requires company context in the API layer.

## Unit normalization

- Electricity: kwh, mwh, wh -> kwh.
- Fuel: liters, gallons -> liters.
- Travel: miles -> km.

## Auditability

- Raw payload retained for traceability.
- Batch metadata shows when the source was ingested.
- AuditLog provides a human decision trail.
