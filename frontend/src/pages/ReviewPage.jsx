import { useEffect, useMemo, useState } from "react";
import {
  approveRecord,
  getRecords,
  getCompanies,
  lockRecord,
  rejectRecord
} from "../api.js";
import RecordsTable from "../components/RecordsTable.jsx";

export default function ReviewPage() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [records, setRecords] = useState([]);
  const [statusFilter, setStatusFilter] = useState("pending");
  const [sourceFilter, setSourceFilter] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const analyst = localStorage.getItem("analystName") || "analyst";

  const activeCompany = useMemo(
    () => companies.find((company) => String(company.id) === String(selectedCompany)),
    [companies, selectedCompany]
  );

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      refreshRecords();
    }
  }, [selectedCompany, statusFilter, sourceFilter]);

  async function loadCompanies() {
    try {
      const data = await getCompanies();
      setCompanies(data);
      if (data[0]) {
        setSelectedCompany(String(data[0].id));
      }
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function refreshRecords() {
    if (!selectedCompany) return;
    try {
      setLoading(true);
      const recordData = await getRecords(selectedCompany, statusFilter, sourceFilter);
      setRecords(recordData);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(recordId) {
    try {
      await approveRecord(recordId, analyst, "Approved in review dashboard");
      await refreshRecords();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleReject(recordId) {
    try {
      await rejectRecord(recordId, analyst, "Flagged for investigation");
      await refreshRecords();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleLock(recordId) {
    try {
      await lockRecord(recordId, analyst, "Locked for audit");
      await refreshRecords();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <div>
      <section className="panel">
        <div className="panel-header">
          <h2>Filters</h2>
        </div>
        <div className="filter-grid">
          <label>
            Company
            <select
              value={selectedCompany}
              onChange={(event) => setSelectedCompany(event.target.value)}
            >
              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Source
            <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
              <option value="">All sources</option>
              <option value="sap">SAP</option>
              <option value="utility">Utility</option>
              <option value="travel">Travel</option>
            </select>
          </label>
          <label>
            Status
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="pending">Pending</option>
              <option value="flagged">Flagged</option>
              <option value="approved">Approved</option>
              <option value="locked">Locked</option>
            </select>
          </label>
        </div>
        {activeCompany && <p className="tenant-tag">{activeCompany.slug}</p>}
        {message && <p className="message">{message}</p>}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Records for review</h2>
          <button className="ghost" onClick={refreshRecords} disabled={loading || !selectedCompany}>
            Refresh
          </button>
        </div>
        <RecordsTable
          records={records}
          onApprove={handleApprove}
          onReject={handleReject}
          onLock={handleLock}
        />
      </section>
    </div>
  );
}
