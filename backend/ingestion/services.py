import csv
import json
from decimal import Decimal, InvalidOperation
from dateutil import parser
from django.utils import timezone

from . import models


SAP_DATE_KEYS = ["Belegdatum", "Posting Date", "Document Date", "Buchungsdatum", "Doc Date"]
SAP_QTY_KEYS = ["Menge", "Quantity", "Qty"]
SAP_UNIT_KEYS = ["ME", "UoM", "Unit"]
SAP_AMOUNT_KEYS = ["Betrag", "Amount", "Value"]
SAP_CURRENCY_KEYS = ["Waehrung", "Currency", "Curr"]
SAP_PLANT_KEYS = ["Werk", "Plant", "Plant Code"]
SAP_SUPPLIER_KEYS = ["Lieferant", "Supplier", "Vendor"]
SAP_DESC_KEYS = ["Material Text", "Description", "Kurztext"]
SAP_REF_KEYS = ["Belegnummer", "Document Number", "Ref", "Doc No"]

UTILITY_START_KEYS = ["billing_period_start", "period_start", "start_date"]
UTILITY_END_KEYS = ["billing_period_end", "period_end", "end_date"]
UTILITY_KWH_KEYS = ["kwh", "usage_kwh", "consumption_kwh"]
UTILITY_METER_KEYS = ["meter_id", "meter"]
UTILITY_TARIFF_KEYS = ["tariff", "rate_plan"]
UTILITY_LOCATION_KEYS = ["location", "site"]


def _get_first(row, keys):
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def _parse_decimal(value):
    if value in (None, ""):
        return None
    try:
        cleaned = str(value).replace(" ", "").replace(",", ".")
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def _parse_date(value):
    if not value:
        return None
    try:
        return parser.parse(value, dayfirst=True).date()
    except (ValueError, TypeError):
        return None


def _normalize_quantity(quantity, unit, category):
    if quantity is None:
        return None, unit
    if not unit:
        return quantity, ""

    unit_key = unit.strip().lower()

    if category == "electricity":
        if unit_key in ["kwh", "kw h", "kilowatthour", "kilowatt-hour"]:
            return quantity, "kwh"
        if unit_key in ["mwh", "mw h"]:
            return quantity * Decimal("1000"), "kwh"
        if unit_key in ["wh"]:
            return quantity * Decimal("0.001"), "kwh"

    if category == "fuel":
        if unit_key in ["l", "liter", "litre", "liters", "litres"]:
            return quantity, "l"
        if unit_key in ["gal", "gallon", "gallons"]:
            return quantity * Decimal("3.78541"), "l"

    if category == "travel":
        if unit_key in ["km", "kilometer", "kilometre"]:
            return quantity, "km"
        if unit_key in ["mi", "mile", "miles"]:
            return quantity * Decimal("1.60934"), "km"

    return quantity, unit_key


def _is_suspicious_fuel(value_liters):
    return value_liters is not None and value_liters > 50000


def _is_suspicious_electricity(value_kwh):
    return value_kwh is not None and (value_kwh < 0 or value_kwh > 100000)


def _is_suspicious_travel(distance_km, origin, destination, unit):
    if origin and destination:
        missing_airport = len(origin) != 3 or len(destination) != 3
    else:
        missing_airport = True
    if unit and unit.strip() == "":
        return True
    if distance_km and distance_km > 15000:
        return True
    return missing_airport


def _normalize_sap(row):
    activity_date = _parse_date(_get_first(row, SAP_DATE_KEYS))
    quantity = _parse_decimal(_get_first(row, SAP_QTY_KEYS))
    unit = _get_first(row, SAP_UNIT_KEYS) or ""
    amount = _parse_decimal(_get_first(row, SAP_AMOUNT_KEYS))
    currency = _get_first(row, SAP_CURRENCY_KEYS) or ""
    location = _get_first(row, SAP_PLANT_KEYS) or ""
    supplier = _get_first(row, SAP_SUPPLIER_KEYS) or ""
    description = (_get_first(row, SAP_DESC_KEYS) or "").lower()

    if "fuel" in description or "diesel" in description or "gasoline" in description:
        activity_type = "fuel"
        scope = "scope1"
    else:
        activity_type = "procurement"
        scope = "scope3"

    normalized_value, normalized_unit = _normalize_quantity(quantity, unit, activity_type)
    suspicious = _is_suspicious_fuel(normalized_value) if activity_type == "fuel" else False

    return {
        "scope_category": scope,
        "activity_type": activity_type,
        "activity_date": activity_date,
        "raw_value": quantity,
        "raw_unit": unit,
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "amount": amount,
        "currency": currency,
        "location": location,
        "supplier": supplier,
        "source_row_id": _get_first(row, SAP_REF_KEYS) or "",
        "is_suspicious": suspicious,
    }


def _normalize_utility(row):
    period_end = _parse_date(_get_first(row, UTILITY_END_KEYS))
    quantity = _parse_decimal(_get_first(row, UTILITY_KWH_KEYS))
    unit = "kwh"
    location = _get_first(row, UTILITY_LOCATION_KEYS) or ""
    meter = _get_first(row, UTILITY_METER_KEYS) or ""
    tariff = _get_first(row, UTILITY_TARIFF_KEYS) or ""

    normalized_value, normalized_unit = _normalize_quantity(quantity, unit, "electricity")
    suspicious = _is_suspicious_electricity(normalized_value)

    return {
        "scope_category": "scope2",
        "activity_type": "electricity",
        "activity_date": period_end,
        "raw_value": quantity,
        "raw_unit": unit,
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "amount": None,
        "currency": "",
        "location": location,
        "supplier": tariff or meter,
        "source_row_id": meter,
        "is_suspicious": suspicious,
    }


def _normalize_travel(row):
    activity_date = _parse_date(row.get("booking_date") or row.get("date"))
    distance = _parse_decimal(row.get("distance"))
    distance_unit = row.get("distance_unit") or row.get("distance_uom") or "km"
    amount = _parse_decimal(row.get("cost") or row.get("amount"))
    currency = row.get("currency") or ""
    origin = row.get("segment_origin") or row.get("origin") or ""
    destination = row.get("segment_destination") or row.get("destination") or ""
    activity_type = row.get("trip_type") or row.get("category") or "travel"
    traveler = row.get("traveler") or row.get("employee") or ""

    normalized_value, normalized_unit = _normalize_quantity(distance, distance_unit, "travel")
    suspicious = _is_suspicious_travel(normalized_value, origin, destination, distance_unit)

    return {
        "scope_category": "scope3",
        "activity_type": activity_type,
        "activity_date": activity_date,
        "raw_value": distance,
        "raw_unit": distance_unit,
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "amount": amount,
        "currency": currency,
        "origin": origin,
        "destination": destination,
        "traveler": traveler,
        "source_row_id": row.get("trip_id", "") or f"{origin}-{destination}",
        "is_suspicious": suspicious,
    }


def _create_batch(company, data_source, ingest_type, file_obj):
    return models.IngestionBatch.objects.create(
        company=company,
        data_source=data_source,
        ingest_type=ingest_type,
        original_filename=getattr(file_obj, "name", ""),
    )


def _finalize_batch(batch, records_total, records_failed, records_suspicious):
    batch.records_total = records_total
    batch.records_failed = records_failed
    batch.records_suspicious = records_suspicious
    batch.status = "processed" if records_failed == 0 else "failed"
    batch.processed_at = timezone.now()
    batch.save(update_fields=[
        "records_total",
        "records_failed",
        "records_suspicious",
        "status",
        "processed_at",
    ])
    return batch


def process_sap_csv(file_obj, company, data_source, ingest_type):
    batch = _create_batch(company, data_source, ingest_type, file_obj)
    decoded = file_obj.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(decoded)

    records_total = 0
    records_failed = 0
    records_suspicious = 0

    for index, row in enumerate(reader, start=1):
        records_total += 1
        raw_record = models.RawRecord.objects.create(
            company=company,
            batch=batch,
            data_source=data_source,
            row_index=index,
            raw_payload=row,
        )
        try:
            normalized = _normalize_sap(row)
            if not normalized.get("activity_date"):
                raise ValueError("Missing activity date")

            record = models.EmissionRecord.objects.create(
                company=company,
                raw_record=raw_record,
                batch=batch,
                data_source=data_source,
                source_row_id=normalized.get("source_row_id", ""),
                scope_category=normalized["scope_category"],
                activity_type=normalized["activity_type"],
                activity_date=normalized["activity_date"],
                raw_value=normalized["raw_value"],
                raw_unit=normalized["raw_unit"],
                normalized_value=normalized["normalized_value"],
                normalized_unit=normalized["normalized_unit"],
                amount=normalized["amount"],
                currency=normalized["currency"],
                location=normalized.get("location", ""),
                supplier=normalized.get("supplier", ""),
                is_suspicious=normalized.get("is_suspicious", False),
                status="flagged" if normalized.get("is_suspicious") else "pending",
            )

            if record.is_suspicious:
                records_suspicious += 1
        except Exception as exc:
            raw_record.status = "failed"
            raw_record.error_message = str(exc)
            raw_record.save(update_fields=["status", "error_message"])
            records_failed += 1

    return _finalize_batch(batch, records_total, records_failed, records_suspicious)


def process_utility_csv(file_obj, company, data_source, ingest_type):
    batch = _create_batch(company, data_source, ingest_type, file_obj)
    decoded = file_obj.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(decoded)

    records_total = 0
    records_failed = 0
    records_suspicious = 0

    for index, row in enumerate(reader, start=1):
        records_total += 1
        raw_record = models.RawRecord.objects.create(
            company=company,
            batch=batch,
            data_source=data_source,
            row_index=index,
            raw_payload=row,
        )
        try:
            normalized = _normalize_utility(row)
            if not normalized.get("activity_date"):
                raise ValueError("Missing billing period end date")

            record = models.EmissionRecord.objects.create(
                company=company,
                raw_record=raw_record,
                batch=batch,
                data_source=data_source,
                source_row_id=normalized.get("source_row_id", ""),
                scope_category=normalized["scope_category"],
                activity_type=normalized["activity_type"],
                activity_date=normalized["activity_date"],
                raw_value=normalized["raw_value"],
                raw_unit=normalized["raw_unit"],
                normalized_value=normalized["normalized_value"],
                normalized_unit=normalized["normalized_unit"],
                amount=normalized["amount"],
                currency=normalized["currency"],
                location=normalized.get("location", ""),
                supplier=normalized.get("supplier", ""),
                is_suspicious=normalized.get("is_suspicious", False),
                status="flagged" if normalized.get("is_suspicious") else "pending",
            )

            if record.is_suspicious:
                records_suspicious += 1
        except Exception as exc:
            raw_record.status = "failed"
            raw_record.error_message = str(exc)
            raw_record.save(update_fields=["status", "error_message"])
            records_failed += 1

    return _finalize_batch(batch, records_total, records_failed, records_suspicious)


def process_travel_json(file_obj, company, data_source, ingest_type):
    batch = _create_batch(company, data_source, ingest_type, file_obj)
    try:
        payload = json.loads(file_obj.read().decode("utf-8"))
        rows = payload.get("records") if isinstance(payload, dict) else payload
    except Exception as exc:
        batch.status = "failed"
        batch.processed_at = timezone.now()
        batch.save(update_fields=["status", "processed_at"])
        raise ValueError("Invalid JSON payload") from exc

    if not isinstance(rows, list):
        batch.status = "failed"
        batch.processed_at = timezone.now()
        batch.save(update_fields=["status", "processed_at"])
        raise ValueError("Travel JSON must be an array or an object with 'records'")

    records_total = 0
    records_failed = 0
    records_suspicious = 0

    for index, row in enumerate(rows, start=1):
        records_total += 1
        raw_record = models.RawRecord.objects.create(
            company=company,
            batch=batch,
            data_source=data_source,
            row_index=index,
            raw_payload=row,
        )
        try:
            normalized = _normalize_travel(row)
            if not normalized.get("activity_date"):
                raise ValueError("Missing booking date")

            record = models.EmissionRecord.objects.create(
                company=company,
                raw_record=raw_record,
                batch=batch,
                data_source=data_source,
                source_row_id=normalized.get("source_row_id", ""),
                scope_category=normalized["scope_category"],
                activity_type=normalized["activity_type"],
                activity_date=normalized["activity_date"],
                raw_value=normalized["raw_value"],
                raw_unit=normalized["raw_unit"],
                normalized_value=normalized["normalized_value"],
                normalized_unit=normalized["normalized_unit"],
                amount=normalized["amount"],
                currency=normalized["currency"],
                origin=normalized.get("origin", ""),
                destination=normalized.get("destination", ""),
                traveler=normalized.get("traveler", ""),
                is_suspicious=normalized.get("is_suspicious", False),
                status="flagged" if normalized.get("is_suspicious") else "pending",
            )

            if record.is_suspicious:
                records_suspicious += 1
        except Exception as exc:
            raw_record.status = "failed"
            raw_record.error_message = str(exc)
            raw_record.save(update_fields=["status", "error_message"])
            records_failed += 1

    return _finalize_batch(batch, records_total, records_failed, records_suspicious)
