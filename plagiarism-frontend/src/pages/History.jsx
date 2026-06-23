import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHistory } from "../api/mockAPI";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetch = async () => {
      const data = await getHistory();
      setHistory(data);
      setLoading(false);
    };
    fetch();
  }, []);

  if (loading) return (
    <div style={{ textAlign: "center", marginTop: "100px", fontSize: "20px" }}>
      Loading history... ⏳
    </div>
  );

  return (
    <div style={{ fontFamily: "Arial", maxWidth: "800px", margin: "40px auto", padding: "0 20px" }}>
      <h1 style={{ color: "#1a1a2e" }}>Past Submissions</h1>

      {history.length === 0 ? (
        <p style={{ color: "#555", marginTop: "20px" }}>No submissions yet.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "30px" }}>
          <thead>
            <tr style={{ background: "#1a1a2e", color: "white" }}>
              <th style={{ padding: "15px", textAlign: "left" }}>Filename</th>
              <th style={{ padding: "15px", textAlign: "left" }}>Score</th>
              <th style={{ padding: "15px", textAlign: "left" }}>Date</th>
              <th style={{ padding: "15px", textAlign: "left" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <tr key={index} style={{ background: index % 2 === 0 ? "#f9f9f9" : "white" }}>
                <td style={{ padding: "15px" }}>{item.filename}</td>
                <td style={{ padding: "15px" }}>
                  <span style={{
                    background: item.overall_score > 60 ? "#e94560" : "#2ecc71",
                    color: "white", padding: "4px 10px", borderRadius: "20px", fontSize: "14px"
                  }}>
                    {item.overall_score}%
                  </span>
                </td>
                <td style={{ padding: "15px", color: "#555" }}>{item.uploaded_at}</td>
                <td style={{ padding: "15px" }}>
                  <button
                    onClick={() => navigate(`/results/${item.submission_id}`)}
                    style={{ padding: "8px 16px", background: "#1a1a2e", color: "white",
                      border: "none", borderRadius: "6px", cursor: "pointer" }}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ textAlign: "center", marginTop: "40px" }}>
        <a href="/upload" style={{ padding: "12px 30px", background: "#e94560",
          color: "white", borderRadius: "8px", textDecoration: "none", fontSize: "16px" }}>
          Upload New Document
        </a>
      </div>
    </div>
  );
}

export default History;