from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("companies/", views.CompanyListCreateView.as_view(), name="companies"),
    path("ingest/", views.IngestView.as_view(), name="ingest"),
    path("batches/", views.BatchListView.as_view(), name="batches"),
    path("records/", views.RecordListView.as_view(), name="records"),
    path("records/<int:record_id>/detail/", views.RecordDetailView.as_view(), name="record-detail"),
    path("records/<int:record_id>/approve/", views.RecordApproveView.as_view(), name="record-approve"),
    path("records/<int:record_id>/reject/", views.RecordRejectView.as_view(), name="record-reject"),
    path("records/<int:record_id>/lock/", views.RecordLockView.as_view(), name="record-lock"),
    path("records/<int:record_id>/", views.RecordUpdateView.as_view(), name="record-update"),
]
