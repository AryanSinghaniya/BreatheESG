import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getRecordDetail, lockRecord } from "../api.js";

export default function RecordDetailPage() {
  const { recordId } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [message, setMessage] = useState("");
  const analyst = localStorage.getItem("analystName") || "analyst";

  useEffect(() => {
    loadDetail();
  }, [recordId]);

  async function loadDetail() {
    try {
      const data = await getRecordDetail(recordId);
      setRecord(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleLock() {
    try {
      await lockRecord(recordId, analyst, "Locked after detail review");
      await loadDetail();
    } catch (error) {
      setMessage(error.message);
    }
  }

  if (!record) {
    return (
      <section className="panel">
        <p className="empty-state">Loading record...</p>
        {message && <p className="message">{message}</p>}
      </section>
    );
  }

  return (
    <div>
      <section className="panel">
        <div className="panel-header">
          <h2>Record detail</h2>
          <button className="ghost" onClick={() => navigate(-1)}>
            Back
          </button>
        </div>
        <div className="detail-grid">
          <div>
            <p className="label">Source</p>
            <p>{record.source_name} ({record.source_type})</p>
          </div>
          <div>
            <p className="label">Scope</p>
            <p>{record.scope_category}</p>
          </div>
          <div>
            <p className="label">Activity</p>
            <p>{record.activity_type}</p>
          </div>
          <div>
            <p className="label">Status</p>
            <p className={`status ${record.status}`}>{record.status}</p>
          </div>
          <div>
            <p className="label">Normalized</p>
            <p>
              {record.normalized_value ?? record.raw_value} {record.normalized_unit || record.raw_unit}
            </p>
          </div>
          <div>
            <p className="label">Location</p>
            <p>{record.location || record.origin || "-"}</p>
          </div>
        </div>
        <button className="primary" onClick={handleLock} disabled={record.locked_for_audit}>
          {record.locked_for_audit ? "Locked for audit" : "Lock for audit"}
        </button>
        {message && <p className="message">{message}</p>}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Raw payload</h2>
        </div>
        <pre className="code-block">{JSON.stringify(record.raw_payload, null, 2)}</pre>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Audit history</h2>
        </div>
        {record.audit_logs.length === 0 ? (
          <p className="empty-state">No audit events yet.</p>
        ) : (
          <div className="table audit">
            <div className="table-row header">
              <span>Field</span>
              <span>Previous</span>
              <span>New</span>
              <span>By</span>
              <span>Reason</span>
              <span>When</span>
            </div>
            {record.audit_logs.map((log) => (
              <div className="table-row" key={log.id}>
                <span>{log.field}</span>
                <span>{log.previous_value || "-"}</span>
                <span>{log.new_value || "-"}</span>
                <span>{log.changed_by || "-"}</span>
                <span>{log.change_reason || "-"}</span>
                <span>{new Date(log.changed_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
