import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../api/mockAPI";

function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first!");
    setLoading(true);
    const response = await uploadDocument(file);
    setLoading(false);
    navigate(`/results/${response.submission_id}`);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "80px", fontFamily: "Arial" }}>
      <h1 style={{ color: "#1a1a2e" }}>Upload Your Document</h1>
      <p style={{ color: "#555" }}>Supported formats: PDF, TXT, DOCX</p>

      <div style={{ marginTop: "40px", padding: "40px", border: "2px dashed #e94560",
        borderRadius: "12px", display: "inline-block", minWidth: "400px" }}>
        <input
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ fontSize: "16px" }}
        />
        {file && (
          <p style={{ marginTop: "15px", color: "#333" }}>
            Selected: <strong>{file.name}</strong>
          </p>
        )}
      </div>

      <br />
      <button
        onClick={handleUpload}
        disabled={loading}
        style={{ marginTop: "30px", padding: "15px 40px", fontSize: "18px",
          background: loading ? "#aaa" : "#e94560", color: "white",
          border: "none", borderRadius: "8px", cursor: loading ? "not-allowed" : "pointer" }}>
        {loading ? "Uploading... please wait" : "Check for Plagiarism"}
      </button>
    </div>
  );
}

export default Upload;