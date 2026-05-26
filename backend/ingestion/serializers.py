from rest_framework import serializers
from . import models


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ["id", "name", "slug", "created_at"]


class IngestionBatchSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="data_source.name", read_only=True)
    source_type = serializers.CharField(source="data_source.source_type", read_only=True)
    ingestion_method = serializers.CharField(source="data_source.ingestion_method", read_only=True)

    class Meta:
        model = models.IngestionBatch
        fields = [
            "id",
            "source_name",
            "source_type",
            "ingestion_method",
            "ingest_type",
            "original_filename",
            "status",
            "ingested_at",
            "processed_at",
            "records_total",
            "records_failed",
            "records_suspicious",
        ]


class EmissionRecordSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="data_source.name", read_only=True)
    source_type = serializers.CharField(source="data_source.source_type", read_only=True)

    class Meta:
        model = models.EmissionRecord
        fields = [
            "id",
            "batch_id",
            "source_name",
            "source_type",
            "scope_category",
            "activity_type",
            "activity_date",
            "raw_value",
            "raw_unit",
            "normalized_value",
            "normalized_unit",
            "status",
            "is_suspicious",
            "approved_by",
            "approved_at",
            "locked_for_audit",
            "location",
            "supplier",
            "currency",
            "amount",
            "origin",
            "destination",
            "traveler",
            "updated_at",
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuditLog
        fields = [
            "id",
            "field",
            "previous_value",
            "new_value",
            "changed_at",
            "changed_by",
            "change_reason",
            "change_type",
        ]


class EmissionRecordDetailSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="data_source.name", read_only=True)
    source_type = serializers.CharField(source="data_source.source_type", read_only=True)
    raw_payload = serializers.JSONField(source="raw_record.raw_payload", read_only=True)
    audit_logs = AuditLogSerializer(source="auditlog_set", many=True, read_only=True)

    class Meta:
        model = models.EmissionRecord
        fields = [
            "id",
            "batch_id",
            "source_name",
            "source_type",
            "source_row_id",
            "scope_category",
            "activity_type",
            "activity_date",
            "raw_value",
            "raw_unit",
            "normalized_value",
            "normalized_unit",
            "status",
            "is_suspicious",
            "approved_by",
            "approved_at",
            "locked_for_audit",
            "location",
            "supplier",
            "currency",
            "amount",
            "origin",
            "destination",
            "traveler",
            "created_at",
            "updated_at",
            "raw_payload",
            "audit_logs",
        ]
