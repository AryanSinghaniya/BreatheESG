import { useEffect, useMemo, useState } from "react";
import { createCompany, getBatches, getCompanies, ingestFile } from "../api.js";
import UploadPanel from "../components/UploadPanel.jsx";
import BatchesTable from "../components/BatchesTable.jsx";

const DEFAULT_COMPANY = {
  name: "Northwind Manufacturing",
  slug: "northwind"
};

export default function UploadPage() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [batches, setBatches] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const activeCompany = useMemo(
    () => companies.find((company) => String(company.id) === String(selectedCompany)),
    [companies, selectedCompany]
  );

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      refreshBatches();
    }
  }, [selectedCompany]);

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

  async function handleCreateDefaultCompany() {
    try {
      const company = await createCompany(DEFAULT_COMPANY);
      setCompanies((prev) => [...prev, company]);
      setSelectedCompany(String(company.id));
      setMessage("Default company created.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function refreshBatches() {
    if (!selectedCompany) return;
    try {
      setLoading(true);
      const batchData = await getBatches(selectedCompany);
      setBatches(batchData);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload({ sourceType, file }) {
    if (!selectedCompany) {
      setMessage("Pick a company first.");
      return;
    }

    const formData = new FormData();
    formData.append("company_id", selectedCompany);
    formData.append("source_type", sourceType);
    formData.append("file", file);

    try {
      setLoading(true);
      await ingestFile(formData);
      await refreshBatches();
      setMessage("Ingestion complete.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <section className="panel">
        <div className="panel-header">
          <h2>Company</h2>
        </div>
        {companies.length === 0 ? (
          <button className="primary" onClick={handleCreateDefaultCompany}>
            Create default company
          </button>
        ) : (
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
        )}
        {activeCompany && <p className="tenant-tag">{activeCompany.slug}</p>}
        {message && <p className="message">{message}</p>}
      </section>

      <UploadPanel onUpload={handleUpload} loading={loading} />

      <section className="panel">
        <div className="panel-header">
          <h2>Ingestion batches</h2>
          <button className="ghost" onClick={refreshBatches} disabled={loading || !selectedCompany}>
            Refresh
          </button>
        </div>
        <BatchesTable batches={batches} />
      </section>
    </div>
  );
}
