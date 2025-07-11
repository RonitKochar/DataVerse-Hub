"use client"; // Required for client-side hooks in Next.js App Router

import React, { useEffect, useState } from "react";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [playChoice, setPlayChoice] = useState<null | "yes" | "no">(null);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<null | "ideal" | "errors">(null);
  const [industry, setIndustry] = useState("");
  const [subdomain, setSubdomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'main' | 'next'>('main');
  const [nextAction, setNextAction] = useState<string | null>(null);
  const [fileInput, setFileInput] = useState<File | null>(null);
  const [filename, setFilename] = useState("");
  const [instruction, setInstruction] = useState("");
  const [nKeep, setNKeep] = useState("");
  const [question, setQuestion] = useState("");
  const [refreshResult, setRefreshResult] = useState<string | null>(null);
  const [stopped, setStopped] = useState(false);
  const [refreshResultNext, setRefreshResultNext] = useState<string | null>(null);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL + "/errors-analysis/";
    fetch(apiUrl)
      .then((res) => {
        if (res.ok) {
          setBackendStatus("✅ Backend is reachable!");
        } else {
          setBackendStatus(`⚠️ Backend error: ${res.status} ${res.statusText}`);
        }
      })
      .catch((err) => {
        setBackendStatus(`❌ Backend not reachable: ${err.message}`);
      });
  }, []);

  const handleRefreshAgent = async () => {
    setLoading(true);
    setRefreshResult(null);
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + "/refresh-agent/", {
        method: "POST",
      });
      const data = await res.json();
      setRefreshResult(JSON.stringify(data));
    } catch (err: any) {
      setRefreshResult("Error: " + err.message);
    }
    setLoading(false);
  };

  const handleRefreshAgentNext = async () => {
    setLoading(true);
    setRefreshResultNext(null);
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + "/refresh-agent/", {
        method: "POST",
      });
      const data = await res.json();
      setRefreshResultNext(JSON.stringify(data));
    } catch (err: any) {
      setRefreshResultNext("Error: " + err.message);
    }
    setLoading(false);
  };

  const handleGenerate = async (type: "ideal" | "errors") => {
    setLoading(true);
    setActionResult(null);
    try {
      const endpoint =
        type === "ideal"
          ? "/generate-ideal-data/"
          : "/generate-data-with-realistic-errors/";
      const formData = new FormData();
      formData.append("industry", industry);
      formData.append("subdomain", subdomain);
      const res = await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + endpoint, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setActionResult(JSON.stringify(data));
    } catch (err: any) {
      setActionResult("Error: " + err.message);
    }
    setLoading(false);
  };

  // Handler for NEXT STEP button
  const handleNextStep = () => {
    setStep('next');
    setActionResult(null);
    setNextAction(null);
    setShowForm(null);
    setIndustry("");
    setSubdomain("");
    setFileInput(null);
    setFilename("");
    setInstruction("");
    setNKeep("");
    setQuestion("");
  };

  // Handlers for new backend endpoints
  const handleNextAction = async (endpoint: string, method: string, body: FormData | null = null) => {
    setLoading(true);
    setActionResult(null);
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_BASE_URL + endpoint, {
        method,
        body: body || undefined,
      });
      let data;
      if (endpoint === '/get-original-sql-contents/') {
        data = await res.text();
      } else {
        data = await res.json();
      }
      setActionResult(typeof data === 'string' ? data : JSON.stringify(data));
    } catch (err: any) {
      setActionResult("Error: " + err.message);
    }
    setLoading(false);
  };

  return (
    <>
      <div style={{ position: "absolute", top: 10, right: 20, fontSize: "0.75rem", color: "#bbb", zIndex: 1000 }}>
        <span>Backend Connection Check: </span>
        <span>{backendStatus}</span>
      </div>
      <main style={{ minHeight: '100vh', background: '#181c24', color: '#f3f3f3', display: "flex", flexDirection: "column", alignItems: "center", marginTop: "3rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: "bold", marginBottom: "2rem", color: '#fff', textShadow: '0 2px 16px #0008' }}>
          {stopped
            ? 'THANKYOU FOR PLAYING 😄🎉'
            : step === 'main'
              ? 'WELCOME TO THE INDUSTRIAL DATA PLAYGROUND'
              : 'HAVING FUN? 😎'}
        </h1>
        <div style={{ width: "100%", background: "#23283a", padding: "1.5rem 0", display: "flex", flexDirection: "column", alignItems: "center", borderRadius: "12px", boxShadow: "0 2px 16px #0006", marginBottom: "2rem", minHeight: 300 }}>
          {stopped ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
              <span style={{ fontSize: '2rem', marginBottom: '1rem' }}>HOPE TO SEE YOU NEXT TIME <span role="img" aria-label="smile">😊</span></span>
            </div>
          ) : actionResult && !loading ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
              <div style={{ marginTop: 16, background: "#23283a", color: '#fff', padding: 12, borderRadius: 6, maxWidth: 400, wordBreak: "break-all", fontSize: 13, boxShadow: '0 1px 8px #0004' }}>
                <strong>Result:</strong>
                <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{actionResult}</pre>
              </div>
              <button className="action-btn" style={{ marginTop: 24, fontSize: "1.1rem", display: "flex", alignItems: "center", gap: 8 }} onClick={handleNextStep}>
                NEXT STEP -&gt; <span role="img" aria-label="excited">😃</span>
              </button>
            </div>
          ) : step === 'main' ? (
            <>
              {playChoice === null && (
                <>
                  <span style={{ fontSize: "1.2rem", fontWeight: 500, marginBottom: "1rem" }}>Want to generate data to play around?</span>
                  <div style={{ display: "flex", gap: "1.5rem" }}>
                    <button className="action-btn" onClick={() => setPlayChoice("yes")}>YES</button>
                    <button className="action-btn" onClick={() => setPlayChoice("no")}>NO</button>
                  </div>
                </>
              )}
              {playChoice === "no" && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <span style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>😢</span>
                  <span style={{ fontSize: "1.1rem", fontWeight: 500 }}>LET'S PLAY NEXT TIME THEN</span>
                </div>
              )}
              {playChoice === "yes" && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1rem", width: "100%" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 500, marginBottom: "0.5rem" }}>Choose an action:</span>
                  {loading && (
                    <div style={{ margin: "12px 0" }}>
                      <span className="spinner" style={{ display: "inline-block", width: 28, height: 28, border: "4px solid #444", borderTop: "4px solid #00e0ff", borderRadius: "50%", animation: "spin 1s linear infinite" }}></span>
                      <span style={{ marginLeft: 10, fontSize: 14, color: "#bbb" }}>Generating...</span>
                    </div>
                  )}
                  <button className="action-btn" style={{ width: 220 }} onClick={handleRefreshAgent} disabled={loading}>Refresh Agent</button>
                  {refreshResult && !loading && (
                    <div style={{ marginTop: 8, background: "#23283a", color: '#fff', padding: 8, borderRadius: 6, maxWidth: 400, wordBreak: "break-all", fontSize: 13, boxShadow: '0 1px 8px #0004' }}>
                      <strong>Result:</strong>
                      <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{refreshResult}</pre>
                    </div>
                  )}
                  <button className="action-btn" style={{ width: 220 }} onClick={() => setShowForm("ideal")} disabled={loading}>Generate Ideal Data</button>
                  <button className="action-btn" style={{ width: 220 }} onClick={() => setShowForm("errors")} disabled={loading}>Generate Data With Errors</button>
                  {(showForm === "ideal" || showForm === "errors") && !loading && (
                    <form
                      onSubmit={e => {
                        e.preventDefault();
                        handleGenerate(showForm);
                      }}
                      style={{ marginTop: 16, display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 260, background: "#23283a", color: '#fff', padding: 16, borderRadius: 8, boxShadow: "0 1px 8px #0004" }}
                    >
                      <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                        Industry:
                        <input
                          type="text"
                          value={industry}
                          onChange={e => setIndustry(e.target.value)}
                          required
                          style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                        />
                      </label>
                      <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                        Subdomain:
                        <input
                          type="text"
                          value={subdomain}
                          onChange={e => setSubdomain(e.target.value)}
                          required
                          style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                        />
                      </label>
                      <button className="action-btn" type="submit" style={{ width: "100%" }} disabled={loading}>
                        {showForm === "ideal" ? "Generate Ideal Data" : "Generate Data With Errors"}
                      </button>
                      <button type="button" className="action-btn" style={{ width: "100%", background: "#444", marginTop: 4 }} onClick={() => setShowForm(null)} disabled={loading}>
                        Cancel
                      </button>
                    </form>
                  )}
                </div>
              )}
            </>
          ) : (
            // NEXT STEP UI
            <>
              <button className="action-btn" style={{ width: 260, marginBottom: 18 }} disabled={loading} onClick={handleRefreshAgentNext}>Refresh Agent</button>
              {refreshResultNext && !loading && (
                <div style={{ marginBottom: 18, background: "#23283a", color: '#fff', padding: 8, borderRadius: 6, maxWidth: 400, wordBreak: "break-all", fontSize: 13, boxShadow: '0 1px 8px #0004' }}>
                  <strong>Result:</strong>
                  <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{refreshResultNext}</pre>
                </div>
              )}
              <span style={{ fontSize: "1.1rem", fontWeight: 500, marginBottom: "1rem" }}>Choose your next adventure:</span>
              {loading && (
                <div style={{ margin: "12px 0" }}>
                  <span className="spinner" style={{ display: "inline-block", width: 28, height: 28, border: "4px solid #444", borderTop: "4px solid #00e0ff", borderRadius: "50%", animation: "spin 1s linear infinite" }}></span>
                  <span style={{ marginLeft: 10, fontSize: 14, color: "#bbb" }}>Generating...</span>
                </div>
              )}
              {/* GET /get-original-sql-contents/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => handleNextAction('/get-original-sql-contents/', 'GET')}>Get Original SQL Contents</button>
              {/* GET /errors-analysis/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => handleNextAction('/errors-analysis/', 'GET')}>Errors Analysis</button>
              {/* GET /missing-values/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => handleNextAction('/missing-values/', 'GET')}>Missing Values</button>
              {/* POST /modify-data-interactive/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => setNextAction('modify-interactive')}>Modify Data Interactive</button>
              {/* POST /modify-data-batch/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => setNextAction('modify-batch')}>Modify Data Batch</button>
              {/* POST /reduce-files/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => setNextAction('reduce-files')}>Reduce Files</button>
              {/* POST /ask-csv-question/ */}
              <button className="action-btn" style={{ width: 260 }} disabled={loading} onClick={() => setNextAction('ask-csv-question')}>Ask CSV Question</button>
              {/* STOP PLAYING BUTTON */}
              <button className="stop-btn" style={{ width: 200, marginTop: 40, background: '#ff2d55', color: '#fff', fontWeight: 700, fontSize: '1.1rem', border: 'none', borderRadius: 8, boxShadow: '0 2px 8px #ff2d5533', letterSpacing: 1, transition: 'background 0.2s', cursor: 'pointer' }} onClick={() => setStopped(true)}>
                STOP PLAYING
              </button>
              {/* Forms for endpoints that require input */}
              {nextAction === 'modify-interactive' && !loading && (
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('filename', filename);
                    formData.append('instruction', instruction);
                    handleNextAction('/modify-data-interactive/', 'POST', formData);
                  }}
                  style={{ marginTop: 16, display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 300, background: "#23283a", color: '#fff', padding: 16, borderRadius: 8, boxShadow: "0 1px 8px #0004" }}
                >
                  <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                    Filename:
                    <input
                      type="text"
                      value={filename}
                      onChange={e => setFilename(e.target.value)}
                      required
                      style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                    />
                  </label>
                  <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                    Instruction:
                    <input
                      type="text"
                      value={instruction}
                      onChange={e => setInstruction(e.target.value)}
                      required
                      style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                    />
                  </label>
                  <button className="action-btn" type="submit" style={{ width: "100%" }} disabled={loading}>Submit</button>
                  <button type="button" className="action-btn" style={{ width: "100%", background: "#444", marginTop: 4 }} onClick={() => setNextAction(null)} disabled={loading}>Cancel</button>
                </form>
              )}
              {nextAction === 'modify-batch' && !loading && (
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    if (!fileInput) return;
                    const formData = new FormData();
                    formData.append('instruction_file', fileInput);
                    handleNextAction('/modify-data-batch/', 'POST', formData);
                  }}
                  style={{ marginTop: 16, display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 300, background: "#23283a", color: '#fff', padding: 16, borderRadius: 8, boxShadow: "0 1px 8px #0004" }}
                >
                  <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                    Instruction File:
                    <input
                      type="file"
                      accept=".txt,.csv,.sql"
                      onChange={e => setFileInput(e.target.files?.[0] || null)}
                      required
                      style={{ width: "100%", marginTop: 4, marginBottom: 8, background: '#181c24', color: '#fff', border: '1px solid #444' }}
                    />
                  </label>
                  <button className="action-btn" type="submit" style={{ width: "100%" }} disabled={loading}>Submit</button>
                  <button type="button" className="action-btn" style={{ width: "100%", background: "#444", marginTop: 4 }} onClick={() => setNextAction(null)} disabled={loading}>Cancel</button>
                </form>
              )}
              {nextAction === 'reduce-files' && !loading && (
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('n_keep', nKeep);
                    handleNextAction('/reduce-files/', 'POST', formData);
                  }}
                  style={{ marginTop: 16, display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 300, background: "#23283a", color: '#fff', padding: 16, borderRadius: 8, boxShadow: "0 1px 8px #0004" }}
                >
                  <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                    Number of files to keep:
                    <input
                      type="number"
                      value={nKeep}
                      onChange={e => setNKeep(e.target.value)}
                      required
                      min={1}
                      style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                    />
                  </label>
                  <button className="action-btn" type="submit" style={{ width: "100%" }} disabled={loading}>Submit</button>
                  <button type="button" className="action-btn" style={{ width: "100%", background: "#444", marginTop: 4 }} onClick={() => setNextAction(null)} disabled={loading}>Cancel</button>
                </form>
              )}
              {nextAction === 'ask-csv-question' && !loading && (
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('question', question);
                    handleNextAction('/ask-csv-question/', 'POST', formData);
                  }}
                  style={{ marginTop: 16, display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 300, background: "#23283a", color: '#fff', padding: 16, borderRadius: 8, boxShadow: "0 1px 8px #0004" }}
                >
                  <label style={{ alignSelf: "flex-start", fontSize: 14 }}>
                    Question:
                    <input
                      type="text"
                      value={question}
                      onChange={e => setQuestion(e.target.value)}
                      required
                      style={{ width: "100%", marginTop: 4, marginBottom: 8, padding: 4, borderRadius: 4, border: "1px solid #444", background: '#181c24', color: '#fff' }}
                    />
                  </label>
                  <button className="action-btn" type="submit" style={{ width: "100%" }} disabled={loading}>Submit</button>
                  <button type="button" className="action-btn" style={{ width: "100%", background: "#444", marginTop: 4 }} onClick={() => setNextAction(null)} disabled={loading}>Cancel</button>
                </form>
              )}
            </>
          )}
        </div>
      </main>
    </>
  );
}
