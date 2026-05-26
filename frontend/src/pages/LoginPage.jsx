import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function handleSubmit(event) {
    event.preventDefault();
    if (!name.trim()) {
      setError("Enter your name to continue.");
      return;
    }
    localStorage.setItem("analystName", name.trim());
    navigate("/upload");
  }

  return (
    <div className="login">
      <div className="login-card">
        <p className="eyebrow">Breathe ESG Prototype</p>
        <h1>Analyst login</h1>
        <p className="subtitle">Use a name to simulate analyst review sessions.</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Analyst name
            <input
              type="text"
              placeholder="Avery Johnson"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </label>
          {error && <p className="message">{error}</p>}
          <button className="primary" type="submit">
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}
