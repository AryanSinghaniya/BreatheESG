export default function BatchesTable({ batches }) {
  if (!batches.length) {
    return <p className="empty-state">No ingestions yet.</p>;
  }

  return (
    <div className="table">
      <div className="table-row header">
        <span>Source</span>
        <span>Method</span>
        <span>Status</span>
        <span>Records</span>
        <span>Failed</span>
        <span>Suspicious</span>
        <span>Ingested</span>
      </div>
      {batches.map((batch) => (
        <div key={batch.id} className="table-row">
          <span>{batch.source_name}</span>
          <span>{batch.ingestion_method}</span>
          <span className={`status ${batch.status}`}>{batch.status}</span>
          <span>{batch.records_total}</span>
          <span>{batch.records_failed}</span>
          <span>{batch.records_suspicious}</span>
          <span>{new Date(batch.ingested_at).toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
