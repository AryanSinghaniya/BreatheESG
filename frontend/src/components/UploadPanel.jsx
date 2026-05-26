import { useState } from "react";

const SOURCE_OPTIONS = [
  { value: "sap", label: "SAP fuel and procurement" },
  { value: "utility", label: "Utility electricity" },
  { value: "travel", label: "Corporate travel" }
];

export default function UploadPanel({ onUpload, loading }) {
  const [sourceType, setSourceType] = useState("sap");
  const [file, setFile] = useState(null);

  const fileAccept = sourceType === "travel" ? ".json,application/json" : ".csv";

  function handleSubmit(event) {
    event.preventDefault();
    if (!file) return;
    onUpload({ sourceType, file });
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Ingest source data</h2>
        <p className="panel-subtitle">Upload a CSV export for one source system at a time.</p>
      </div>
      <form className="upload-form" onSubmit={handleSubmit}>
        <label>
          Source
          <select value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
            {SOURCE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          {sourceType === "travel" ? "JSON file" : "CSV file"}
          <input
            type="file"
            accept={fileAccept}
            onChange={(event) => setFile(event.target.files[0])}
          />
        </label>
        <button className="primary" type="submit" disabled={!file || loading}>
          {loading ? "Working..." : "Upload and normalize"}
        </button>
      </form>
      <div className="hint">
        <p>Sample files live in the sample-data folder in this repo.</p>
        {sourceType === "travel" ? (
          <p>Travel ingestion expects a JSON array or an object with a records array.</p>
        ) : null}
      </div>
    </section>
  );
}
