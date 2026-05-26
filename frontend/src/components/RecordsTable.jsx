import { Link } from "react-router-dom";

export default function RecordsTable({ records, onApprove, onReject, onLock }) {
  if (!records.length) {
    return <p className="empty-state">No records found for this filter.</p>;
  }

  return (
    <div className="table records">
      <div className="table-row header">
        <span>Activity</span>
        <span>Scope</span>
        <span>Date</span>
        <span>Normalized</span>
        <span>Status</span>
        <span>Location</span>
        <span>Risk</span>
        <span>Action</span>
      </div>
      {records.map((record) => {
        const isLocked = record.status === "locked";
        const canLock = record.status === "approved";

        return (
          <div key={record.id} className="table-row">
            <span>{record.activity_type}</span>
            <span>{record.scope_category}</span>
            <span>{record.activity_date}</span>
            <span>
              {record.normalized_value ?? record.raw_value} {record.normalized_unit || record.raw_unit}
            </span>
            <span className={`status ${record.status}`}>{record.status}</span>
            <span>{record.location || record.supplier || record.origin || "-"}</span>
            <span className={record.is_suspicious ? "risk high" : "risk low"}>
              {record.is_suspicious ? "Suspicious" : "OK"}
            </span>
            <span className="actions">
              <Link className="ghost" to={`/records/${record.id}`}>
                View
              </Link>
              <button className="ghost" onClick={() => onApprove(record.id)} disabled={isLocked}>
                Approve
              </button>
              <button className="ghost" onClick={() => onReject(record.id)} disabled={isLocked}>
                Reject
              </button>
              <button className="ghost" onClick={() => onLock(record.id)} disabled={!canLock}>
                Lock
              </button>
            </span>
          </div>
        );
      })}
    </div>
  );
}
