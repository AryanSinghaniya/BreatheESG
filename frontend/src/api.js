const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(payload.error || "Request failed");
  }
  return response.json();
}

export function getCompanies() {
  return request("/api/companies/");
}

export function createCompany(data) {
  return request("/api/companies/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

export function ingestFile(formData) {
  return request("/api/ingest/", {
    method: "POST",
    body: formData
  });
}

export function getBatches(companyId) {
  const query = companyId ? `?company_id=${companyId}` : "";
  return request(`/api/batches/${query}`);
}

export function getRecords(companyId, statusFilter, sourceType) {
  const params = new URLSearchParams();
  if (companyId) params.append("company_id", companyId);
  if (statusFilter) params.append("status", statusFilter);
  if (sourceType) params.append("source_type", sourceType);
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/api/records/${query}`);
}

export function getRecordDetail(recordId) {
  return request(`/api/records/${recordId}/detail/`);
}

export function approveRecord(recordId, reviewer, note) {
  return request(`/api/records/${recordId}/approve/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviewer, note })
  });
}

export function rejectRecord(recordId, reviewer, note) {
  return request(`/api/records/${recordId}/reject/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviewer, note })
  });
}

export function lockRecord(recordId, reviewer, note) {
  return request(`/api/records/${recordId}/lock/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviewer, note })
  });
}
