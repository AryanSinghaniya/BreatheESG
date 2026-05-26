from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers, services


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class CompanyListCreateView(APIView):
    def get(self, request):
        companies = models.Company.objects.all().order_by("name")
        return Response(serializers.CompanySerializer(companies, many=True).data)

    def post(self, request):
        serializer = serializers.CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response(serializers.CompanySerializer(company).data, status=status.HTTP_201_CREATED)


class IngestView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        company_id = request.data.get("company_id")
        source_type = request.data.get("source_type")
        ingest_type = request.data.get("ingest_type", "file")
        upload = request.data.get("file")

        if not company_id or not source_type or not upload:
            return Response(
                {"error": "company_id, source_type, and file are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = models.Company.objects.filter(id=company_id).first()
        if not company:
            return Response({"error": "company not found"}, status=status.HTTP_404_NOT_FOUND)

        ingestion_method = "json" if source_type == "travel" else "csv"
        data_source, _ = models.DataSource.objects.get_or_create(
            company=company,
            source_type=source_type,
            defaults={
                "name": f"{source_type.title()} source",
                "ingestion_method": ingestion_method,
            },
        )
        if data_source.ingestion_method != ingestion_method:
            data_source.ingestion_method = ingestion_method
            data_source.save(update_fields=["ingestion_method"])

        try:
            if source_type == "sap":
                batch = services.process_sap_csv(upload, company, data_source, ingest_type)
            elif source_type == "utility":
                batch = services.process_utility_csv(upload, company, data_source, ingest_type)
            elif source_type == "travel":
                batch = services.process_travel_json(upload, company, data_source, ingest_type)
            else:
                return Response({"error": "unsupported source_type"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializers.IngestionBatchSerializer(batch).data)


class BatchListView(APIView):
    def get(self, request):
        company_id = request.query_params.get("company_id")
        batches = models.IngestionBatch.objects.all().order_by("-ingested_at")
        if company_id:
            batches = batches.filter(company_id=company_id)
        return Response(serializers.IngestionBatchSerializer(batches, many=True).data)


class RecordListView(APIView):
    def get(self, request):
        company_id = request.query_params.get("company_id")
        source_type = request.query_params.get("source_type")
        status_filter = request.query_params.get("status")
        records = models.EmissionRecord.objects.all().order_by("-updated_at")
        if company_id:
            records = records.filter(company_id=company_id)
        if source_type:
            records = records.filter(data_source__source_type=source_type)
        if status_filter:
            records = records.filter(status=status_filter)
        return Response(serializers.EmissionRecordSerializer(records, many=True).data)


class RecordDetailView(APIView):
    def get(self, request, record_id):
        record = models.EmissionRecord.objects.filter(id=record_id).first()
        if not record:
            return Response({"error": "record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializers.EmissionRecordDetailSerializer(record).data)


class RecordApproveView(APIView):
    def post(self, request, record_id):
        reviewer = request.data.get("reviewer", "analyst")
        record = models.EmissionRecord.objects.filter(id=record_id).first()
        if not record:
            return Response({"error": "record not found"}, status=status.HTTP_404_NOT_FOUND)

        if record.locked_for_audit:
            return Response({"error": "record is locked"}, status=status.HTTP_409_CONFLICT)

        previous_status = record.status
        record.status = "approved"
        record.approved_at = timezone.now()
        record.approved_by = reviewer
        record.save(update_fields=["status", "approved_at", "approved_by"])

        models.AuditLog.objects.create(
            emission_record=record,
            field="status",
            previous_value=previous_status,
            new_value=record.status,
            changed_by=reviewer,
            change_reason=request.data.get("note", ""),
            change_type="status",
        )

        return Response(serializers.EmissionRecordSerializer(record).data)


class RecordRejectView(APIView):
    def post(self, request, record_id):
        reviewer = request.data.get("reviewer", "analyst")
        record = models.EmissionRecord.objects.filter(id=record_id).first()
        if not record:
            return Response({"error": "record not found"}, status=status.HTTP_404_NOT_FOUND)

        if record.locked_for_audit:
            return Response({"error": "record is locked"}, status=status.HTTP_409_CONFLICT)

        previous_status = record.status
        record.status = "flagged"
        record.approved_at = None
        record.approved_by = ""
        record.save(update_fields=["status", "approved_at", "approved_by"])

        models.AuditLog.objects.create(
            emission_record=record,
            field="status",
            previous_value=previous_status,
            new_value=record.status,
            changed_by=reviewer,
            change_reason=request.data.get("note", ""),
            change_type="status",
        )

        return Response(serializers.EmissionRecordSerializer(record).data)


class RecordLockView(APIView):
    def post(self, request, record_id):
        reviewer = request.data.get("reviewer", "analyst")
        record = models.EmissionRecord.objects.filter(id=record_id).first()
        if not record:
            return Response({"error": "record not found"}, status=status.HTTP_404_NOT_FOUND)

        if record.status != "approved":
            return Response({"error": "record must be approved first"}, status=status.HTTP_409_CONFLICT)

        record.status = "locked"
        record.locked_for_audit = True
        record.save(update_fields=["status", "locked_for_audit"])

        models.AuditLog.objects.create(
            emission_record=record,
            field="locked_for_audit",
            previous_value="False",
            new_value="True",
            changed_by=reviewer,
            change_reason=request.data.get("note", ""),
            change_type="lock",
        )

        return Response(serializers.EmissionRecordSerializer(record).data)


class RecordUpdateView(APIView):
    def patch(self, request, record_id):
        reviewer = request.data.get("reviewer", "analyst")
        record = models.EmissionRecord.objects.filter(id=record_id).first()
        if not record:
            return Response({"error": "record not found"}, status=status.HTTP_404_NOT_FOUND)

        if record.locked_for_audit:
            return Response({"error": "record is locked"}, status=status.HTTP_409_CONFLICT)

        allowed_fields = [
            "activity_date",
            "raw_value",
            "raw_unit",
            "normalized_value",
            "normalized_unit",
            "amount",
            "currency",
            "location",
            "supplier",
            "origin",
            "destination",
            "traveler",
        ]

        for field in allowed_fields:
            if field in request.data:
                previous_value = getattr(record, field)
                new_value = request.data.get(field)
                setattr(record, field, new_value)
                models.AuditLog.objects.create(
                    emission_record=record,
                    field=field,
                    previous_value=str(previous_value),
                    new_value=str(new_value),
                    changed_by=reviewer,
                    change_reason=request.data.get("change_reason", "manual edit"),
                    change_type="edit",
                )

        record.save()
        return Response(serializers.EmissionRecordSerializer(record).data)
