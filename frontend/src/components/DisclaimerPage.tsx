import { useEffect, useState } from "react";
import { fetchDisclaimer } from "../api";

export default function DisclaimerPage() {
  const [text, setText]   = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDisclaimer().then(d => setText(d.text)).catch(e => setError(String(e)));
  }, []);

  return (
    <div style={{ maxWidth: 680 }}>
      <div className="label" style={{ marginBottom: 16 }}>Disclaimer</div>
      {error && <p style={{ color: "var(--red)", fontSize: 12, marginBottom: 12 }}>{error}</p>}
      <div style={{
        background: "var(--bg-surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius-md)", padding: "20px 24px",
      }}>
        <pre style={{
          whiteSpace: "pre-wrap", fontSize: 12, lineHeight: 1.8,
          color: "var(--text-secondary)", fontFamily: "var(--font-mono)",
        }}>
          {text}
        </pre>
      </div>
    </div>
  );
}
