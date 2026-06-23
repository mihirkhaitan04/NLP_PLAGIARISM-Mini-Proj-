import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav style={{ background: "#1a1a2e", padding: "15px 30px", display: "flex", gap: "30px", alignItems: "center" }}>
      <span style={{ color: "#e94560", fontWeight: "bold", fontSize: "20px" }}>
        PlagDetect
      </span>
      <Link to="/" style={{ color: "white", textDecoration: "none" }}>Home</Link>
      <Link to="/upload" style={{ color: "white", textDecoration: "none" }}>Upload</Link>
      <Link to="/history" style={{ color: "white", textDecoration: "none" }}>History</Link>
    </nav>
  );
}

export default Navbar;