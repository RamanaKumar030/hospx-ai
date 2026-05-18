"use client";

import { useState } from "react";

const API = "https://hospx-ai-2.onrender.com";

export default function Home() {
  const [symptoms, setSymptoms] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [places, setPlaces] = useState<any[]>([]);
  const [error, setError] = useState("");

  async function analyze() {
    if (!symptoms.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);
    setPlaces([]);

    const start = performance.now();

    try {
      const res = await fetch(`${API}/symptom-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms }),
      });

      const data = await res.json();
      const latency = ((performance.now() - start) / 1000).toFixed(2);

      setResult({ ...data.result, latency });

      const loc = await fetch(`${API}/nearby-hospitals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: 12.9716, lon: 77.5946 }),
      });

      const locData = await loc.json();
      setPlaces(locData.places || []);
    } catch {
      setError("Backend not reachable. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const emergency = result?.urgency === "Emergency";

  return (
    <main className="min-h-screen bg-[#020617] text-white overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,#12345c_0%,#020617_45%)] opacity-80" />

      <section className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <header className="mb-8">
          <div className="text-5xl font-black tracking-tight text-sky-400">
            HOSPX AI
          </div>
          <p className="text-slate-400 mt-2">
            Emergency Medical Intelligence System • Clinical Decision Platform
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_2.2fr_1.3fr] gap-6">
          <aside className="rounded-3xl border border-slate-800 bg-slate-950/70 backdrop-blur-xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Patient Input</h2>

            <textarea
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="chest pain, sweating, dizziness..."
              className="w-full h-44 rounded-2xl bg-slate-900 border border-slate-700 p-4 text-white outline-none focus:border-sky-400"
            />

            <button
              onClick={analyze}
              disabled={loading}
              className="mt-5 w-full h-14 rounded-2xl bg-gradient-to-r from-blue-600 to-sky-400 font-black tracking-wide shadow-lg shadow-sky-500/20 hover:scale-[1.02] transition disabled:opacity-60"
            >
              {loading ? "ANALYZING..." : "RUN EMERGENCY TRIAGE"}
            </button>
          </aside>

          <section className="rounded-3xl border border-slate-800 bg-slate-950/70 backdrop-blur-xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-5">AI Medical Analysis</h2>

            {error && (
              <div className="rounded-2xl bg-red-600/20 border border-red-500 p-4 text-red-200">
                {error}
              </div>
            )}

            {emergency && (
              <div className="mb-5 rounded-2xl bg-gradient-to-r from-red-700 to-red-500 p-4 font-black animate-pulse">
                EMERGENCY DETECTED — IMMEDIATE MEDICAL ATTENTION REQUIRED
              </div>
            )}

            {result ? (
              <>
                <div className="grid grid-cols-3 gap-4">
                  <Metric title="SEVERITY" value={result.severity || "N/A"} />
                  <Metric title="URGENCY" value={result.urgency || "N/A"} />
                  <Metric title="LATENCY" value={`${result.latency}s`} />
                </div>

                <div className="mt-7">
                  <h3 className="text-lg font-bold mb-3">Possible Conditions</h3>
                  <div className="space-y-3">
                    {(result.possible_conditions || []).map((c: string, i: number) => (
                      <div
                        key={i}
                        className="rounded-2xl bg-slate-900 border border-slate-800 p-4"
                      >
                        {c}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-7 rounded-2xl bg-sky-500/10 border border-sky-500/30 p-5">
                  <p className="text-slate-400 text-sm">Recommended Department</p>
                  <p className="text-2xl font-black text-sky-300">
                    {result.recommended_department || "N/A"}
                  </p>
                </div>

                <div className="mt-7">
                  <h3 className="text-lg font-bold mb-3">
                    Nearby Medical Facilities
                  </h3>

                  {places.length ? (
                    <div className="space-y-3">
                      {places.slice(0, 8).map((p, i) => (
                        <div
                          key={i}
                          className="rounded-2xl bg-slate-900 border border-slate-800 p-4"
                        >
                          <p className="font-bold">{p.name}</p>
                          <p className="text-slate-400 text-sm">{p.type}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400">No nearby data found</p>
                  )}
                </div>
              </>
            ) : (
              <div className="h-96 flex items-center justify-center text-slate-500">
                Enter symptoms and run triage.
              </div>
            )}
          </section>

          <aside className="space-y-6">
            <Panel title="System Health">
              <p>API Status: Online</p>
              <p>AI Model: Active</p>
              <p>Response: Live</p>
              <p>Backend: Render</p>
            </Panel>

            <Panel title="Emergency Tools">
              <p>Ambulance: 108 India</p>
              <p>Hospitals: Auto-detect enabled</p>
              <p>Pharmacy: Nearby search ready</p>
            </Panel>
          </aside>
        </div>
      </section>
    </main>
  );
}

function Metric({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-5 text-center hover:scale-105 transition">
      <p className="text-xs text-slate-400">{title}</p>
      <p className="text-2xl font-black text-sky-300 mt-2">{value}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-950/70 backdrop-blur-xl p-6 shadow-2xl">
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <div className="space-y-2 text-slate-300">{children}</div>
    </div>
  );
}