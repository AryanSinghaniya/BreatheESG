import { NavLink, Outlet, useNavigate } from "react-router-dom";

export default function Shell() {
  const navigate = useNavigate();
  const analyst = localStorage.getItem("analystName") || "Analyst";

  function handleLogout() {
    localStorage.removeItem("analystName");
    navigate("/login");
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">Breathe ESG Prototype</p>
          <h1>Enterprise ingestion, normalized and review-ready.</h1>
        </div>
        <div className="topbar-card">
          <p className="label">Signed in as</p>
          <strong>{analyst}</strong>
          <button className="ghost" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </header>

      <nav className="nav">
        <NavLink to="/upload" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Upload Dashboard
        </NavLink>
        <NavLink to="/review" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Review Dashboard
        </NavLink>
      </nav>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
