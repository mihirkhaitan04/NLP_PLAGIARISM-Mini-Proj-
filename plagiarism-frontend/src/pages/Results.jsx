import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getResults } from "../api/mockAPI";

function Results() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let intervalId;
    const fetch = async () => {
      const data = await getResults(id);
      if (data.status === "processing") {
        setResult({ status: "processing" });
      } else {
        setResult(data);
        setLoading(false);
        if (intervalId) clearInterval(intervalId);
      }
    };
    fetch();
    intervalId = setInterval(fetch, 2000);
    return () => clearInterval(intervalId);
  }, [id]);

  if (loading || (result && result.status === "processing")) return (
    <div style={{ textAlign: "center", marginTop: "100px", fontSize: "20px" }}>
      <div style={{ marginBottom: "20px", fontSize: "40px" }}>⚙️</div>
      Analyzing your document with AI...<br/>
      <span style={{ fontSize: "14px", color: "#888" }}>(This may take a few moments. Your document is safely in the background queue!)</span>
    </div>
  );

  // Determine AI verdict color and label
  const aiDetails = result.ai_detection_details || {};
  const getVerdictStyle = (verdict) => {
    switch (verdict) {
      case "likely_ai": return { color: "#e94560", label: "Likely AI-Generated" };
      case "mixed": return { color: "#f5a623", label: "Mixed / Uncertain" };
      case "likely_human": return { color: "#2ecc71", label: "Likely Human-Written" };
      default: return { color: "#888", label: "Unknown" };
    }
  };
  const verdictStyle = getVerdictStyle(aiDetails.verdict);

  return (
    <div style={{ fontFamily: "Arial", maxWidth: "800px", margin: "40px auto", padding: "0 20px" }}>
      <h1 style={{ color: "#1a1a2e" }}>Results for: {result.filename}</h1>

      {/* Score Cards */}
      <div style={{ display: "flex", gap: "20px", marginTop: "30px" }}>
        <div style={{ flex: 1, background: "#e94560", color: "white",
          borderRadius: "12px", padding: "25px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", fontWeight: "bold" }}>{result.overall_score}%</div>
          <div style={{ fontSize: "16px", marginTop: "8px" }}>Overall Plagiarism</div>
        </div>
        <div style={{ flex: 1, background: "#f5a623", color: "white",
          borderRadius: "12px", padding: "25px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", fontWeight: "bold" }}>{result.ai_generated_score}%</div>
          <div style={{ fontSize: "16px", marginTop: "8px" }}>AI Generated</div>
        </div>
        <div style={{ flex: 1, background: "#1a1a2e", color: "white",
          borderRadius: "12px", padding: "25px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", fontWeight: "bold" }}>{result.paraphrased_score}%</div>
          <div style={{ fontSize: "16px", marginTop: "8px" }}>Paraphrased</div>
        </div>
      </div>

      {/* AI Detection Details Panel */}
      {aiDetails.verdict && (
        <div style={{
          marginTop: "25px", padding: "20px", borderRadius: "12px",
          background: "#f8f9fa", border: "1px solid #e0e0e0"
        }}>
          <h3 style={{ margin: "0 0 12px 0", color: "#1a1a2e" }}>AI Content Analysis</h3>
          <div style={{ display: "flex", gap: "30px", flexWrap: "wrap" }}>
            <div>
              <span style={{ color: "#888", fontSize: "13px" }}>Verdict</span>
              <div style={{ fontWeight: "bold", fontSize: "16px", color: verdictStyle.color, marginTop: "2px" }}>
                {verdictStyle.label}
              </div>
            </div>
            {aiDetails.perplexity !== null && (
              <div>
                <span style={{ color: "#888", fontSize: "13px" }}>Perplexity (GPT-2)</span>
                <div style={{ fontWeight: "bold", fontSize: "16px", color: "#333", marginTop: "2px" }}>
                  {aiDetails.perplexity}
                </div>
              </div>
            )}
            <div>
              <span style={{ color: "#888", fontSize: "13px" }}>Burstiness</span>
              <div style={{ fontWeight: "bold", fontSize: "16px", color: "#333", marginTop: "2px" }}>
                {aiDetails.burstiness} {aiDetails.burstiness > 0.5 ? "(Human-like)" : "(AI-like)"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Flagged Sections */}
      <h2 style={{ marginTop: "40px", color: "#1a1a2e" }}>Flagged Sections</h2>
      {result.flagged_sections.length === 0 && (
        <p style={{ color: "#555", fontStyle: "italic" }}>No plagiarism detected. Your document looks original!</p>
      )}
      {result.flagged_sections.map((section, index) => (
        <div key={index} style={{
          marginTop: "15px", padding: "20px", borderRadius: "10px", borderLeft: "5px solid",
          borderColor: section.source === "web" ? "#e94560" : "#f5a623",
          background: section.source === "web" ? "#fff0f2" : "#fff8ee" }}>

          {/* Header row with badge and confidence */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ fontWeight: "bold", color: section.source === "web" ? "#e94560" : "#f5a623" }}>
                {section.type === "ai_generated" ? "AI Generated" : "Paraphrased"}
              </span>
              {/* Source Badge */}
              <span style={{
                padding: "3px 10px", borderRadius: "12px", fontSize: "11px",
                fontWeight: "bold", color: "white",
                background: section.source === "web" ? "#e94560" : "#f5a623"
              }}>
                {section.source === "web" ? "Web Source" : "Local DB"}
              </span>
            </div>
            <span style={{ color: "#888", fontSize: "14px" }}>
              Confidence: {Math.round(section.confidence * 100)}%
            </span>
          </div>

          {/* Flagged text */}
          <p style={{ color: "#333", margin: 0 }}>{section.text}</p>

          {/* Source URL (only shown for web matches) */}
          {section.source === "web" && section.source_url && (
            <div style={{ marginTop: "10px", fontSize: "13px" }}>
              <span style={{ color: "#888" }}>Source: </span>
              <a
                href={section.source_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#1a73e8", textDecoration: "none" }}
              >
                {section.source_title || section.source_url}
              </a>
            </div>
          )}
        </div>
      ))}

      {/* Check Another */}
      <div style={{ textAlign: "center", marginTop: "40px", marginBottom: "40px" }}>
        <a href="/upload" style={{ padding: "12px 30px", background: "#1a1a2e",
          color: "white", borderRadius: "8px", textDecoration: "none", fontSize: "16px" }}>
          Check Another Document
        </a>
      </div>
    </div>
  );
}

export default Results;