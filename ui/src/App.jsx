import { useState, useCallback, useRef } from "react";

const API_URL = "/api/extract";

function SpinnerIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  );
}

const EXAMPLES = [
  {
    title: "Supported Formats",
    desc: "Upload JPEG, PNG, or WebP images of vehicles. The clearer the plate, the better the results.",
  },
  {
    title: "How It Works",
    desc: "Uses EasyOCR with pattern matching to detect and extract license plate text from vehicle images.",
  },
  {
    title: "Best Practices",
    desc: "Use well-lit, front or rear photos. Avoid extreme angles. Crop to focus on the vehicle if possible.",
  },
];

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFile = useCallback((f) => {
    if (!f) return;
    setFile(f);
    setResults(null);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f?.type.startsWith("image/")) handleFile(f);
  }, [handleFile]);

  const extract = useCallback(async () => {
    if (!file || loading) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const fd = new FormData();
      fd.append("image", file);
      const res = await fetch(API_URL, { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${res.status}`);
      }
      setResults(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [file, loading]);

  const reset = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 flex flex-col items-center px-4 pt-20 pb-12 max-w-lg mx-auto w-full">
        {/* Title */}
        <div className="text-center mb-10">
          <h1 className="text-2xl font-bold tracking-tight mb-1">
            AutoPlate Pro
          </h1>
          <p className="text-sm text-text-secondary">
            Extract license plates from any vehicle image
          </p>
        </div>

        <input
          ref={inputRef}
          id="image-upload"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />

        {/* Upload / Preview */}
        {!preview ? (
          <label
            htmlFor="image-upload"
            onDrop={onDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            className={`w-full rounded-xl border-2 border-dashed cursor-pointer flex flex-col items-center justify-center py-16 transition-colors ${
              dragOver
                ? "border-accent bg-surface"
                : "border-border hover:border-border-hover hover:bg-surface"
            }`}
          >
            <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p className="text-sm font-medium text-text">
              Drop image or click to upload
            </p>
            <p className="text-xs text-text-muted mt-1">JPEG, PNG, WebP</p>
          </label>
        ) : (
          <div className="w-full animate-in">
            <div className="rounded-xl overflow-hidden border border-border bg-surface">
              <img
                src={preview}
                alt="Vehicle"
                className="w-full max-h-[360px] object-contain"
              />
            </div>

            <div className="flex gap-2 mt-3">
              <button
                id="btn-extract"
                onClick={extract}
                disabled={loading}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                  loading
                    ? "bg-surface text-text-muted"
                    : "bg-accent text-white hover:bg-accent-hover"
                }`}
              >
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <SpinnerIcon className="w-3.5 h-3.5 animate-spin" />
                    Analyzing…
                  </span>
                ) : (
                  "Extract Plates"
                )}
              </button>
              <button
                onClick={reset}
                className="px-4 py-2.5 rounded-lg text-sm font-medium bg-surface text-text-secondary hover:bg-surface-hover transition-colors cursor-pointer"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="w-full mt-4 px-4 py-3 rounded-lg bg-red-50 border border-red-200 animate-in">
            <p className="text-sm text-danger">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="w-full mt-6 space-y-2 animate-in">
            <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-3">
              {results.total === 0
                ? "No plates detected"
                : `${results.total} plate${results.total > 1 ? "s" : ""} detected`}
            </p>

            {results.plates.map((plate, i) => (
              <div
                key={i}
                className="flex items-center gap-3 px-4 py-3.5 rounded-lg bg-surface border border-border"
              >
                {i === 0 && (
                  <span className="w-1.5 h-1.5 rounded-full bg-success shrink-0" />
                )}
                <span className="text-base font-semibold tracking-[0.12em]">
                  {plate}
                </span>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Bottom Section — Examples & Info */}
      <section className="border-t border-border bg-surface/50">
        <div className="max-w-3xl mx-auto px-4 py-12">
          <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-6 text-center">
            How to use
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {EXAMPLES.map((item, i) => (
              <div key={i} className="px-5 py-4 rounded-xl bg-bg border border-border">
                <p className="text-sm font-medium text-text mb-1">{item.title}</p>
                <p className="text-xs text-text-secondary leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-xs text-text-muted mt-8">
            Powered by EasyOCR · FastAPI · React
          </p>
        </div>
      </section>
    </div>
  );
}
