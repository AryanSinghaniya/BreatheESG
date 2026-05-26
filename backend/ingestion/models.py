from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DataSource(models.Model):
    SOURCE_CHOICES = [
        ("sap", "SAP"),
        ("utility", "Utility"),
        ("travel", "Travel"),
    ]
    INGESTION_CHOICES = [
        ("csv", "CSV"),
        ("json", "JSON"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    ingestion_method = models.CharField(max_length=10, choices=INGESTION_CHOICES)
    name = models.CharField(max_length=200)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.slug}::{self.name}"


class IngestionBatch(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("processed", "Processed"),
        ("failed", "Failed"),
    ]
    INGEST_CHOICES = [
        ("file", "File"),
        ("api", "API"),
        ("manual", "Manual"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    ingest_type = models.CharField(max_length=20, choices=INGEST_CHOICES)
    original_filename = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    ingested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    records_total = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    records_suspicious = models.IntegerField(default=0)

    def __str__(self):
        return f"Batch {self.id} ({self.data_source.name})"


class RawRecord(models.Model):
    STATUS_CHOICES = [
        ("parsed", "Parsed"),
        ("failed", "Failed"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    row_index = models.IntegerField()
    raw_payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="parsed")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EmissionRecord(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("flagged", "Flagged"),
        ("approved", "Approved"),
        ("locked", "Locked"),
    ]
    SCOPE_CHOICES = [
        ("scope1", "Scope 1"),
        ("scope2", "Scope 2"),
        ("scope3", "Scope 3"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE)
    raw_record = models.ForeignKey(RawRecord, on_delete=models.SET_NULL, null=True, blank=True)
    source_row_id = models.CharField(max_length=200, blank=True)
    scope_category = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    activity_type = models.CharField(max_length=120)
    activity_date = models.DateField()
    raw_value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    raw_unit = models.CharField(max_length=40, blank=True)
    normalized_value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    normalized_unit = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_suspicious = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=120, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    locked_for_audit = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    origin = models.CharField(max_length=10, blank=True)
    destination = models.CharField(max_length=10, blank=True)
    traveler = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuditLog(models.Model):
    CHANGE_CHOICES = [
        ("edit", "Edit"),
        ("status", "Status"),
        ("lock", "Lock"),
    ]

    emission_record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE)
    field = models.CharField(max_length=120)
    previous_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=120, blank=True)
    change_reason = models.TextField(blank=True)
    change_type = models.CharField(max_length=20, choices=CHANGE_CHOICES, default="edit")
