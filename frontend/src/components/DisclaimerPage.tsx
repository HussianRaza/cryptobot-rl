import { useEffect, useState } from "react";
import { fetchDisclaimer } from "../api";

export default function DisclaimerPage() {
  const [text, setText] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetchDisclaimer()
      .then(d => setText(d.text))
      .catch(e => setError(String(e)));
  }, []);

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h2 style={{ color: "#a0c4ff" }}>Disclaimer</h2>
      {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}
      <pre style={{ whiteSpace: "pre-wrap", color: "#ccc", lineHeight: 1.6 }}>{text}</pre>
    </div>
  );
}
