import { useState } from "react";
import {
  Upload,
  FileSearch,
  CheckCircle,
  AlertTriangle,
  Loader2,
  ShieldCheck,
  UserRound,
  ScanSearch,
} from "lucide-react";

type ScreeningResult = {
  success: boolean;
  filename: string;
  document_type: string;
  ocr_confidence: string;

  extracted_data?: {
    name?: string;
    date_of_birth?: string;
    document_number?: string;
  };

  validation?: {
    status: string;
    risk_level: string;
    validation_score: number;
    risk_score: number;
    recommendation: string;

    checks: {
      check: string;
      status: string;
      message: string;
    }[];
  };

  image_analysis?: {
    status: string;
    risk_level: string;
    tampering_score: number;
    image_quality: string;

    resolution: {
      width: number;
      height: number;
    };

    checks: {
      check: string;
      status: string;
      message: string;
    }[];
  };

  face_analysis?: {
    status: string;
    face_detected: boolean;
    face_count: number;
    face_quality: string;
    risk_level: string;
    message: string;

    face_location?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };

  security_assessment?: {
    status: string;
    risk_level: string;
    risk_score: number;
    recommendation: string;
  };

  raw_text?: string;
  message?: string;
};

export default function NewScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError("");
    }
  };

  const analyzeDocument = async () => {
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        "http://127.0.0.1:8000/screen-document",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned status ${response.status}`
        );
      }

      const data: ScreeningResult = await response.json();

if (!data.success) {
  throw new Error(
    data.message || "Document processing failed."
  );
}

// Save result to screening history
const history = JSON.parse(
  localStorage.getItem("borderguard_history") || "[]"
);

const riskScore =
  data.security_assessment?.risk_score ??
  data.validation?.risk_score ??
  0;

const status =
  riskScore >= 80
    ? "HIGH RISK"
    : riskScore >= 40
    ? "REVIEW"
    : "VERIFIED";

history.push({
  id: `#BG-${10233 + history.length}`,
  name: data.extracted_data?.name || "Unknown Applicant",
  applicant: data.extracted_data?.name || "Unknown Applicant",
  documentType: data.document_type,
  document_type: data.document_type,
  riskScore: riskScore,
  risk_score: riskScore,
  riskLevel:
    data.security_assessment?.risk_level ||
    data.validation?.risk_level ||
    "LOW",
  status: status,
  date: new Date().toLocaleDateString(),
});

localStorage.setItem(
  "borderguard_history",
  JSON.stringify(history)
);

setResult(data);

      // Save screening result to history
const historyRecord = {
  id: `#BG-${Date.now()}`,
  filename: data.filename,
  documentType: data.document_type,
  riskScore: data.security_assessment?.risk_score ?? 0,
  riskLevel: data.security_assessment?.risk_level ?? "LOW",
  status:
    data.security_assessment?.status === "VERIFIED"
      ? "VERIFIED"
      : "REVIEW",
  date: new Date().toLocaleDateString(),
};

// Get existing history
const existingHistory = JSON.parse(
  localStorage.getItem("borderguard_history") || "[]"
);

// Add newest screening at the beginning
existingHistory.unshift(historyRecord);

// Save updated history
localStorage.setItem(
  "borderguard_history",
  JSON.stringify(existingHistory)
);

// Display result
setResult(data);;
    } catch (err) {
      console.error("Backend connection error:", err);

      setError(
        "Could not connect to BorderGuard AI backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8 text-white">

      <div className="mx-auto max-w-6xl">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="mb-8">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-600 p-3">
              <FileSearch size={26} />
            </div>

            <div>

              <h1 className="text-3xl font-bold">
                New Document Screening
              </h1>

              <p className="mt-1 text-slate-400">
                Upload a passport, Aadhaar card, national ID,
                driving licence or visa for AI-based screening.
              </p>

            </div>

          </div>

        </div>

        {/* ================================================= */}
        {/* UPLOAD CARD */}
        {/* ================================================= */}

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold">
            Upload Document
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Select an image of an identity or travel document.
          </p>

          <div className="mt-6">

            <label
              htmlFor="document-upload"
              className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-950 p-10 transition hover:border-blue-500"
            >

              <Upload
                size={42}
                className="mb-4 text-blue-500"
              />

              <p className="font-medium">
                Select Document
              </p>

              <p className="mt-1 text-sm text-slate-500">
                JPG, JPEG or PNG
              </p>

              <input
                id="document-upload"
                type="file"
                accept=".jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />

            </label>

          </div>

          {/* SELECTED FILE */}

          {file && (
            <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Selected file
              </p>

              <p className="mt-1 font-medium text-blue-400">
                {file.name}
              </p>

            </div>
          )}

          {/* ERROR */}

          {error && (
            <div className="mt-5 flex items-start gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4">

              <AlertTriangle
                size={20}
                className="mt-0.5 text-red-400"
              />

              <p className="text-sm text-red-400">
                {error}
              </p>

            </div>
          )}

          {/* ANALYZE BUTTON */}

          <button
            onClick={analyzeDocument}
            disabled={!file || loading}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {loading ? (
              <>
                <Loader2
                  size={18}
                  className="animate-spin"
                />

                Analyzing Document...
              </>
            ) : (
              <>
                <FileSearch size={18} />

                Analyze Document
              </>
            )}

          </button>

        </div>

        {/* ================================================= */}
        {/* RESULTS */}
        {/* ================================================= */}

        {result && (
          <div className="mt-8 space-y-6">

            {/* ================================================= */}
            {/* SECURITY ASSESSMENT */}
            {/* ================================================= */}

            {result.security_assessment && (
              <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-6">

                <div className="flex items-center gap-3">

                  <ShieldCheck
                    size={30}
                    className="text-green-400"
                  />

                  <div>

                    <h2 className="text-xl font-bold text-green-400">
                      Security Assessment
                    </h2>

                    <p className="text-sm text-slate-400">
                      {result.security_assessment.recommendation}
                    </p>

                  </div>

                </div>

                <div className="mt-6 grid gap-4 md:grid-cols-3">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Security Status
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.status}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Risk Level
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.risk_level}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Risk Score
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.risk_score} / 100
                    </p>

                  </div>

                </div>

              </div>
            )}

            {/* ================================================= */}
            {/* DOCUMENT INFORMATION */}
            {/* ================================================= */}

            <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">

              <h2 className="text-xl font-bold">
                Document Information
              </h2>

              <div className="mt-5 grid gap-4 md:grid-cols-3">

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <p className="text-xs text-slate-500">
                    Filename
                  </p>

                  <p className="mt-2 font-medium">
                    {result.filename}
                  </p>

                </div>

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <p className="text-xs text-slate-500">
                    Document Type
                  </p>

                  <p className="mt-2 font-semibold text-blue-400">
                    {result.document_type}
                  </p>

                </div>

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <p className="text-xs text-slate-500">
                    OCR Status
                  </p>

                  <p className="mt-2 font-semibold text-green-400">
                    {result.ocr_confidence}
                  </p>

                </div>

              </div>

            </div>

            {/* ================================================= */}
            {/* OCR EXTRACTED INFORMATION */}
            {/* ================================================= */}

            {result.extracted_data && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">

                <h2 className="text-xl font-bold">
                  OCR Extracted Information
                </h2>

                <div className="mt-5 grid gap-4 md:grid-cols-3">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Name
                    </p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.name ||
                        "Not detected"}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Date of Birth
                    </p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.date_of_birth ||
                        "Not detected"}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Document Number
                    </p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.document_number ||
                        "Not detected"}
                    </p>

                  </div>

                </div>

              </div>
            )}

            {/* ================================================= */}
            {/* DOCUMENT VALIDATION */}
            {/* ================================================= */}

            {result.validation && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">

                <h2 className="text-xl font-bold">
                  Document Validation
                </h2>

                <div className="mt-5 grid gap-4 md:grid-cols-3">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Validation Status
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.validation.status}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Validation Score
                    </p>

                    <p className="mt-2 font-bold">
                      {result.validation.validation_score} / 100
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Risk Score
                    </p>

                    <p className="mt-2 font-bold">
                      {result.validation.risk_score} / 100
                    </p>

                  </div>

                </div>

                <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <p className="text-xs text-slate-500">
                    Recommendation
                  </p>

                  <p className="mt-2 text-sm text-slate-300">
                    {result.validation.recommendation}
                  </p>

                </div>

                <div className="mt-5 space-y-3">

                  {result.validation.checks.map(
                    (check, index) => (
                      <div
                        key={index}
                        className="rounded-lg border border-slate-700 bg-slate-950 p-4"
                      >

                        <div className="flex items-center gap-2">

                          <CheckCircle
                            size={18}
                            className="text-green-400"
                          />

                          <p className="font-medium">
                            {check.check}
                          </p>

                          <span className="ml-auto text-xs font-bold text-green-400">
                            {check.status}
                          </span>

                        </div>

                        <p className="mt-1 text-sm text-slate-400">
                          {check.message}
                        </p>

                      </div>
                    )
                  )}

                </div>

              </div>
            )}

            {/* ================================================= */}
            {/* IMAGE & TAMPERING ANALYSIS */}
            {/* ================================================= */}

            {result.image_analysis && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">

                <div className="flex items-center gap-3">

                  <ScanSearch
                    size={26}
                    className="text-blue-400"
                  />

                  <h2 className="text-xl font-bold">
                    Image & Tampering Analysis
                  </h2>

                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-4">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Image Quality
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.image_analysis.image_quality}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Tampering Score
                    </p>

                    <p className="mt-2 font-bold">
                      {result.image_analysis.tampering_score} / 100
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Tampering Status
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.image_analysis.status}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Resolution
                    </p>

                    <p className="mt-2 font-bold">
                      {result.image_analysis.resolution.width}
                      {" × "}
                      {result.image_analysis.resolution.height}
                    </p>

                  </div>

                </div>

                <div className="mt-5 space-y-3">

                  {result.image_analysis.checks.map(
                    (check, index) => (
                      <div
                        key={index}
                        className="rounded-lg border border-slate-700 bg-slate-950 p-4"
                      >

                        <div className="flex items-center gap-2">

                          <CheckCircle
                            size={18}
                            className="text-green-400"
                          />

                          <p className="font-medium">
                            {check.check}
                          </p>

                          <span className="ml-auto text-xs font-bold text-green-400">
                            {check.status}
                          </span>

                        </div>

                        <p className="mt-1 text-sm text-slate-400">
                          {check.message}
                        </p>

                      </div>
                    )
                  )}

                </div>

              </div>
            )}

            {/* ================================================= */}
            {/* FACE DETECTION */}
            {/* ================================================= */}

            {result.face_analysis && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">

                <div className="flex items-center gap-3">

                  <UserRound
                    size={26}
                    className="text-purple-400"
                  />

                  <h2 className="text-xl font-bold">
                    Face Detection Analysis
                  </h2>

                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-4">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Status
                    </p>

                    <p
                      className={`mt-2 font-bold ${
                        result.face_analysis.face_detected
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      {result.face_analysis.status}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Faces Detected
                    </p>

                    <p className="mt-2 font-bold">
                      {result.face_analysis.face_count}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Face Quality
                    </p>

                    <p className="mt-2 font-bold">
                      {result.face_analysis.face_quality}
                    </p>

                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Risk Level
                    </p>

                    <p className="mt-2 font-bold">
                      {result.face_analysis.risk_level}
                    </p>

                  </div>

                </div>

                <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <p className="text-sm text-slate-300">
                    {result.face_analysis.message}
                  </p>

                </div>

                {result.face_analysis.face_location && (
                  <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-xs text-slate-500">
                      Detected Face Location
                    </p>

                    <p className="mt-2 text-sm text-slate-300">
                      X: {result.face_analysis.face_location.x}
                      {" | "}
                      Y: {result.face_analysis.face_location.y}
                      {" | "}
                      Width: {result.face_analysis.face_location.width}
                      {" | "}
                      Height: {result.face_analysis.face_location.height}
                    </p>

                  </div>
                )}

              </div>
            )}

            {/* ================================================= */}
            {/* RAW OCR TEXT */}
            {/* ================================================= */}

            {result.raw_text && (
              <details className="rounded-xl border border-slate-700 bg-slate-900 p-6">

                <summary className="cursor-pointer text-sm font-medium text-blue-400 hover:text-blue-300">
                  View Raw OCR Text
                </summary>

                <div className="mt-4 max-h-80 overflow-auto rounded-lg border border-slate-700 bg-slate-950 p-4">

                  <pre className="whitespace-pre-wrap text-xs leading-5 text-slate-400">
                    {result.raw_text}
                  </pre>

                </div>

              </details>
            )}

            {/* ================================================= */}
            {/* SUCCESS MESSAGE */}
            {/* ================================================= */}

            <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4 text-center">

              <p className="text-sm text-green-400">
                ✓ {result.message}
              </p>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}