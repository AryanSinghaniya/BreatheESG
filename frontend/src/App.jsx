import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import ReviewPage from "./pages/ReviewPage.jsx";
import RecordDetailPage from "./pages/RecordDetailPage.jsx";
import Shell from "./components/Shell.jsx";

function RequireAnalyst({ children }) {
  const analyst = localStorage.getItem("analystName");
  if (!analyst) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <RequireAnalyst>
              <Shell />
            </RequireAnalyst>
          }
        >
          <Route index element={<Navigate to="/upload" replace />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="review" element={<ReviewPage />} />
          <Route path="records/:recordId" element={<RecordDetailPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/upload" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
