from django.contrib import admin
from . import models


admin.site.register(models.Company)
admin.site.register(models.DataSource)
admin.site.register(models.IngestionBatch)
admin.site.register(models.RawRecord)
admin.site.register(models.EmissionRecord)
admin.site.register(models.AuditLog)
