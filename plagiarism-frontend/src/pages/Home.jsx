import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();
  return (
    <div style={{ textAlign: "center", marginTop: "100px", fontFamily: "Arial" }}>
      <h1 style={{ fontSize: "40px", color: "#1a1a2e" }}>AI Plagiarism Detector</h1>
      <p style={{ fontSize: "18px", color: "#555", marginTop: "20px" }}>
        Detect paraphrased and AI-generated plagiarism in academic documents.
      </p>
      <button
        onClick={() => navigate("/upload")}
        style={{ marginTop: "40px", padding: "15px 40px", fontSize: "18px",
          background: "#e94560", color: "white", border: "none",
          borderRadius: "8px", cursor: "pointer" }}>
        Check Your Document
      </button>
    </div>
  );
}

export default Home;