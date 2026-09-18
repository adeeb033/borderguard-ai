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
  face_detection: any;
  success: boolean;
  filename: string;
  document_type: string;
  ocr_confidence: string;
  verification?: {
    document_number?: string;
    found: boolean;
    message?: string;

    reference_data?: {
      document_type?: string;
      full_name?: string;
      date_of_birth?: string;
      nationality?: string;
      expiry_date?: string;
      gender?: string;
      status?: string;
    };

    comparison?: {
      [field: string]: {
        label: string;
        ocr_value: string | null;
        reference_value: string | null;
        status: string;
      };
    };
  };

  extracted_data?: {
    name?: string;
    date_of_birth?: string;
    document_number?: string;
    visa_type?: string;
    entry_validation?: string;
    stay_duration?: string;
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



  forensic_analysis?: {
  status: string;
  risk_level: string;
  forensic_risk_score: number;
  metadata: {
    format: string;
    width: number;
    height: number;
    metadata_present: boolean;
    findings: string[];
  };
  ela: {
    ela_score: number;
    max_difference: number;
    high_difference_ratio: number;
  };
  noise_analysis: {
    noise_mean: number;
    noise_variation: number;
    suspicious: boolean;
  };
  image_quality: {
    width: number;
    height: number;
    sharpness: number;
    brightness: number;
    contrast: number;
  };
  findings: string[];
  message: string;
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
    risk_reasons?: string[];
    components?: {
      validation_risk: number;
      tampering_risk: number;
      forensic_risk: number;
      ocr_risk: number;
      face_risk: number;
      reference_risk: number;
    };

    discrepancy_analysis?: {
      count: number;
      severity: string;
      summary: string;

      items: {
        field: string;
        ocr_value: string | null;
        reference_value: string | null;
        status: string;
      }[];
    };
  };

  raw_text?: string;
  message?: string;
};

export default function NewScreening() {
  const [officerNotes, setOfficerNotes] = useState("");
  const [officerReviewStatus, setOfficerReviewStatus] = useState<
    "PENDING" | "REVIEWED" | "FLAGGED"
  >("PENDING");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [liveFace, setLiveFace] = useState<File | null>(null);
  const [faceVerification, setFaceVerification] = useState<any>(null);
  const [faceVerificationLoading, setFaceVerificationLoading] = useState(false);
  const [faceVerificationError, setFaceVerificationError] = useState("");

  const [faceVerificationDecision, setFaceVerificationDecision] = useState<
    "MATCH" | "MISMATCH" | null
  >(null);

  const faceMismatch =
    faceVerification?.status === "MISMATCH" ||
    faceVerification?.reference_face_verification?.status === "MISMATCH";

  const officerScreeningStatus = faceMismatch
    ? "REVIEW REQUIRED"
    : result?.security_assessment?.status || "REVIEW REQUIRED";

  const officerRiskLevel = faceMismatch
    ? "MEDIUM"
    : result?.security_assessment?.risk_level || "UNKNOWN";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
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

      const response = await fetch("http://127.0.0.1:8000/screen-document", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend returned status ${response.status}`);
      }

      const data: ScreeningResult = await response.json();
      console.log("FULL SCREENING RESPONSE:", data);

      if (!data.success) {
        throw new Error(data.message || "Document processing failed.");
      }

      setResult(data);
    } catch (err) {
      console.error("SCREENING ERROR:", err);

      setError(
        err instanceof Error ? err.message : "An unexpected error occurred.",
      );
    } finally {
      setLoading(false);
    }
  };
  const verifyFace = async () => {
    if (!file) {
      setFaceVerificationError("Please upload a document first.");
      return;
    }

    if (!liveFace) {
      setFaceVerificationError("Please upload a live face image first.");
      return;
    }

    setFaceVerificationLoading(true);
    setFaceVerificationError("");
    setFaceVerification(null);

    try {
      const formData = new FormData();

      formData.append("document_face", file);
      formData.append("live_face", liveFace);

      formData.append(
        "document_number",
        result?.extracted_data?.document_number ||
          result?.verification?.document_number ||
          "",
      );
      console.log(
        "FACE VERIFICATION DOCUMENT NUMBER:",
        result?.extracted_data?.document_number ||
          result?.verification?.document_number ||
          "",
      );

      const response = await fetch(
        "http://127.0.0.1:8000/face-verification/verify",
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) {
        throw new Error(
          `Face verification failed with status ${response.status}`,
        );
      }

      const data = await response.json();

      console.log("FACE VERIFICATION RESPONSE:", data);

      if (!data.success) {
        throw new Error(data.message || "Face verification failed.");
      }

      setFaceVerification(data);
      setFaceVerificationDecision(
        data.status === "MATCH" ? "MATCH" : "MISMATCH",
      );
    } catch (err) {
      console.error("FACE VERIFICATION ERROR:", err);

      setFaceVerificationError(
        err instanceof Error ? err.message : "An unexpected error occurred.",
      );
    } finally {
      setFaceVerificationLoading(false);
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

            <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 p-3 text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.12)]">
              <FileSearch size={26} />
            </div>

            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">
                New Document Screening
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                AI-powered screening for identity and travel documents.
              </p>
            </div>

          </div>
        </div>


        {/* ================================================= */}
        {/* UPLOAD CARD */}
        {/* ================================================= */}

        <div className="rounded-xl border border-slate-800/80 bg-[#080c10]/90 p-6 shadow-[0_0_30px_rgba(0,0,0,0.18)]">

          <div className="flex items-center justify-between">

            <div>

              <div className="flex items-center gap-2">

                <span className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.7)]" />

                <h2 className="text-lg font-semibold text-white">
                  Document Intake
                </h2>

              </div>

              <p className="mt-1 text-sm text-slate-500">
                Upload an identity or travel document for automated security screening.
              </p>

            </div>

            <span className="hidden rounded-md border border-slate-800 bg-slate-950 px-3 py-1 text-[10px] uppercase tracking-wider text-slate-500 sm:block">
              AI SCREENING
            </span>

          </div>


          <div className="mt-6">

            <label
              htmlFor="document-upload"
              className="group flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-[#05080b] p-10 transition-all duration-200 hover:border-blue-500/60 hover:bg-blue-500/[0.03]"
            >

              <div className="rounded-xl border border-blue-500/20 bg-blue-500/10 p-4 transition group-hover:border-blue-500/40 group-hover:bg-blue-500/15">

                <Upload
                  size={38}
                  className="text-blue-400"
                />

              </div>


              <p className="mt-4 font-semibold text-slate-200">
                Select Document
              </p>

              <p className="mt-1 text-sm text-slate-500">
                Passport • Aadhaar • Visa • Driving Licence
              </p>

              <p className="mt-2 text-[11px] uppercase tracking-wider text-slate-600">
                JPG • JPEG • PNG
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
            <div className="mt-5 flex items-center justify-between rounded-lg border border-blue-500/20 bg-blue-500/[0.04] p-4">

              <div>

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Selected Document
                </p>

                <p className="mt-1 font-medium text-blue-400">
                  {file.name}
                </p>

              </div>


              <div className="rounded-md border border-green-500/20 bg-green-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-green-400">
                Ready
              </div>

            </div>
          )}

        </div>

          {/* ================================================= */}
          {/* FACE VERIFICATION */}
          {/* ================================================= */}

          {file && (
            <div className="mt-5 rounded-xl border border-slate-700 bg-slate-950 p-5">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-blue-600/20 p-2">
                  <UserRound size={22} className="text-blue-400" />
                </div>

                <div>
                  <h3 className="font-semibold">Traveller Face Verification</h3>

                  <p className="text-sm text-slate-400">
                    Compare the traveller's face with the face detected on the
                    uploaded document.
                  </p>
                </div>
              </div>

              <div className="mt-5">
                <label
                  htmlFor="live-face-upload"
                  className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-900 p-8 transition hover:border-blue-500"
                >
                  <UserRound size={38} className="mb-3 text-blue-500" />

                  <p className="font-medium">Upload Traveller Face</p>

                  <p className="mt-1 text-sm text-slate-500">
                    JPG, JPEG or PNG
                  </p>

                  <input
                    id="live-face-upload"
                    type="file"
                    accept=".jpg,.jpeg,.png"
                    className="hidden"
                    onChange={(event) => {
                      const selectedFile = event.target.files?.[0];

                      if (selectedFile) {
                        setLiveFace(selectedFile);
                        setFaceVerification(null);
                        setFaceVerificationDecision(null);
                        setFaceVerificationError("");
                      }
                    }}
                  />
                </label>
              </div>

              {liveFace && (
                <div className="mt-4 rounded-lg border border-slate-700 bg-slate-900 p-4">
                  <p className="text-xs text-slate-500">
                    Selected traveller image
                  </p>

                  <p className="mt-1 font-medium text-blue-400">
                    {liveFace.name}
                  </p>
                </div>
              )}

              {faceVerificationError && (
                <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
                  <p className="text-sm text-red-400">
                    {faceVerificationError}
                  </p>
                </div>
              )}

              <button
                onClick={verifyFace}
                disabled={!result || !liveFace || faceVerificationLoading}
                className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {faceVerificationLoading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Verifying Face...
                  </>
                ) : (
                  <>
                    <ScanSearch size={18} />
                    Verify Traveller Face
                  </>
                )}
              </button>
            </div>
          )}

          {/* ERROR */}

          {error && (
            <div className="mt-5 flex items-start gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
              <AlertTriangle size={20} className="mt-0.5 text-red-400" />

              <p className="text-sm text-red-400">{error}</p>
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
                <Loader2 size={18} className="animate-spin" />
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

                {/* HEADER */}
                <div className="flex items-center gap-3">
                  <ShieldCheck size={30} className="text-green-400" />

                  <div>
                    <h2 className="text-xl font-bold text-green-400">
                      Security Assessment
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                      {result.security_assessment.recommendation}
                    </p>
                  </div>
                </div>

                {/* STATUS / RISK / SCORE */}
                <div className="mt-6 grid gap-4 md:grid-cols-3">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                      Security Status
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.status}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                      Risk Level
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.risk_level}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                      Risk Score
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.security_assessment.risk_score} / 100
                    </p>
                  </div>

                </div>

                {/* ================================================= */}
                {/* EXPLAINABLE AI */}
                {/* ================================================= */}

                {result.security_assessment.risk_reasons &&
                  result.security_assessment.risk_reasons.length > 0 && (
                    <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

                      <div className="flex items-center justify-between">

                        <div>
                          <p className="text-sm font-semibold text-blue-400">
                            Why this decision?
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            Key factors considered by the screening engine.
                          </p>
                        </div>

                        <span className="rounded-md border border-blue-500/20 bg-blue-500/10 px-2 py-1 text-[9px] font-semibold uppercase tracking-wider text-blue-400">
                          Explainable AI
                        </span>

                      </div>

                      <div className="mt-4 space-y-2">

                        {result.security_assessment.risk_reasons.map(
                          (reason, index) => (
                            <div
                              key={index}
                              className="flex items-start gap-3 rounded-md border border-slate-800 bg-[#080c10] px-3 py-2"
                            >
                              <span className="mt-0.5 text-green-400">
                                ✓
                              </span>

                              <span className="text-sm text-slate-300">
                                {reason}
                              </span>
                            </div>
                          ),
                        )}

                      </div>

                    </div>
                  )}

                {/* ================================================= */}
                {/* RISK COMPONENTS */}
                {/* ================================================= */}

                {result.security_assessment.components && (
                  <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

                    <p className="text-sm font-semibold text-blue-400">
                      Risk Components
                    </p>

                    <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          Validation Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.validation_risk}/100
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          Tampering Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.tampering_risk}/100
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          Forensic Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.forensic_risk}/100
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          OCR Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.ocr_risk}/100
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          Face Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.face_risk}/100
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 p-3">
                        <p className="text-xs text-slate-500">
                          Reference Risk
                        </p>

                        <p className="mt-1 font-bold text-blue-400">
                          {result.security_assessment.components.reference_risk}/100
                        </p>
                      </div>

                    </div>

                    <p className="mt-3 text-xs text-slate-500">
                      Final risk is calculated using weighted contributions
                      from validation, tampering, forensic analysis, OCR,
                      face detection, and reference verification.
                    </p>

                  </div>
                )}

              </div>
            )}

            {/* ================================================= */}
            {/* FACE VERIFICATION RESULT */}
            {/* ================================================= */}

            {faceVerification && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-600/20 p-2">
                    <UserRound size={24} className="text-blue-400" />
                  </div>

                  <div>
                    <h2 className="text-xl font-bold">
                      Face Verification Result
                    </h2>

                    <p className="text-sm text-slate-400">
                      Similarity-based comparison between the traveller and
                      document face.
                    </p>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  {/* STATUS */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Verification Status
                    </p>

                    <p
                      className={`mt-2 font-bold ${
                        faceVerification.status === "MATCH"
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      {faceVerification.status}
                    </p>
                  </div>

                  {/* CONFIDENCE */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Confidence</p>

                    <p className="mt-2 font-bold text-blue-400">
                      {faceVerification.confidence}%
                    </p>
                  </div>

                  {/* MODEL */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Verification Model</p>

                    <p className="mt-2 font-bold text-blue-400">
                      {faceVerification.model}
                    </p>
                  </div>
                </div>

                {/* REFERENCE FACE VERIFICATION */}

                {faceVerification.reference_face_verification && (
                  <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Traveller ↔ Reference Face
                    </p>

                    <div className="mt-3 grid gap-4 md:grid-cols-3">
                      <div>
                        <p className="text-xs text-slate-500">Reference Face</p>

                        <p className="mt-1 font-bold text-blue-400">
                          {faceVerification.reference_face_verification
                            .available
                            ? "FOUND"
                            : "NOT AVAILABLE"}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-500">
                          Verification Status
                        </p>

                        <p
                          className={`mt-1 font-bold ${
                            faceVerification.reference_face_verification
                              .status === "MATCH"
                              ? "text-green-400"
                              : faceVerification.reference_face_verification
                                    .status === "MISMATCH"
                                ? "text-red-400"
                                : "text-yellow-400"
                          }`}
                        >
                          {faceVerification.reference_face_verification.status}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-500">Confidence</p>

                        <p className="mt-1 font-bold text-blue-400">
                          {faceVerification.reference_face_verification
                            .confidence !== null &&
                          faceVerification.reference_face_verification
                            .confidence !== undefined
                            ? `${faceVerification.reference_face_verification.confidence}%`
                            : "N/A"}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* MESSAGE */}

                <div
                  className={`mt-5 rounded-lg border p-4 ${
                    faceVerificationDecision === "MISMATCH"
                      ? "border-red-500/30 bg-red-500/10"
                      : "border-slate-700 bg-slate-950"
                  }`}
                >
                  <p
                    className={`text-sm ${
                      faceVerificationDecision === "MISMATCH"
                        ? "text-red-400"
                        : "text-slate-300"
                    }`}
                  >
                    {faceVerification.message}
                  </p>

                  {faceVerificationDecision === "MISMATCH" && (
                    <p className="mt-2 text-sm font-medium text-red-400">
                      ⚠ Face mismatch detected. Manual officer review is
                      required.
                    </p>
                  )}
                </div>

                {/* IMPORTANT DISCLAIMER */}

                <div className="mt-4 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-4">
                  <p className="text-xs text-yellow-400">
                    Face verification is a similarity-based assistance feature.
                    It does not by itself prove identity or document
                    authenticity. Final decisions remain with the authorized
                    officer.
                  </p>
                </div>
              </div>
            )}

            {/* ================================================= */}
            {/* OVERALL SCREENING SUMMARY */}
            {/* ================================================= */}

            {result && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-green-600/20 p-2">
                    <ShieldCheck size={24} className="text-green-400" />
                  </div>

                  <div>
                    <h2 className="text-xl font-bold">
                      Overall Screening Summary
                    </h2>

                    <p className="text-sm text-slate-400">
                      Consolidated result from document, reference and face
                      verification checks.
                    </p>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {/* DOCUMENT SCREENING */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Document Screening</p>

                    <p
                      className={`mt-2 font-bold ${
                        result.security_assessment?.status === "VERIFIED"
                          ? "text-green-400"
                          : "text-yellow-400"
                      }`}
                    >
                      {result.security_assessment?.status || "NOT AVAILABLE"}
                    </p>
                  </div>

                  {/* REFERENCE VERIFICATION */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Reference Verification
                    </p>

                    <p
                      className={`mt-2 font-bold ${
                        result.verification?.found
                          ? "text-green-400"
                          : "text-yellow-400"
                      }`}
                    >
                      {result.verification?.found ? "FOUND" : "NOT FOUND"}
                    </p>
                  </div>

                  {/* FACE VERIFICATION */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Traveller ↔ Document Face
                    </p>

                    <p
                      className={`mt-2 font-bold ${
                        faceVerification?.status === "MATCH"
                          ? "text-green-400"
                          : faceVerification?.status === "MISMATCH"
                            ? "text-red-400"
                            : "text-slate-400"
                      }`}
                    >
                      {faceVerification?.status || "NOT CHECKED"}
                    </p>
                  </div>

                  {/* REFERENCE FACE */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Traveller ↔ Reference Face
                    </p>

                    <p
                      className={`mt-2 font-bold ${
                        faceVerification?.reference_face_verification
                          ?.status === "MATCH"
                          ? "text-green-400"
                          : faceVerification?.reference_face_verification
                                ?.status === "MISMATCH"
                            ? "text-red-400"
                            : "text-slate-400"
                      }`}
                    >
                      {faceVerification?.reference_face_verification?.status ||
                        "NOT CHECKED"}
                    </p>
                  </div>

                  {/* OFFICER DECISION */}

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Officer Decision</p>

                    <p
  className={`mt-2 font-bold ${
    officerReviewStatus === "REVIEWED"
      ? "text-green-400"
      : officerReviewStatus === "FLAGGED"
      ? "text-red-400"
      : officerScreeningStatus === "REVIEW REQUIRED"
      ? "text-yellow-400"
      : officerScreeningStatus === "VERIFIED"
      ? "text-green-400"
      : "text-red-400"
  }`}
>
  {officerReviewStatus === "PENDING"
    ? officerScreeningStatus
    : officerReviewStatus}
</p>
                  </div>
                </div>

                {/* OFFICER DECISION NOTICE */}

                <div className="mt-5 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-4">
                  <p className="text-sm text-yellow-400">
                    AI screening provides supporting evidence only. The final
                    decision must be made by an authorized officer after
                    reviewing the available evidence.
                  </p>
                </div>
              </div>
            )}

            {/* ================================================= */}
            {/* DOCUMENT INFORMATION */}
            {/* ================================================= */}

            <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Document Information</h2>

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">Filename</p>

                  <p className="mt-2 font-medium">{result.filename}</p>
                </div>

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">Document Type</p>

                  <p className="mt-2 font-semibold text-blue-400">
                    {result.document_type}
                  </p>
                </div>

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">OCR Status</p>

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
                <h2 className="text-xl font-bold">OCR Extracted Information</h2>

                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Name</p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.name || "Not detected"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Date of Birth</p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.date_of_birth || "Not detected"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Document Number</p>

                    <p className="mt-2 font-medium">
                      {result.extracted_data.document_number || "Not detected"}
                    </p>
                  </div>
                  {result.document_type === "Visa" && (
                    <>
                      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                        <p className="text-xs text-slate-500">Visa Type</p>

                        <p className="mt-2 font-medium">
                          {result.extracted_data.visa_type || "Not detected"}
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                        <p className="text-xs text-slate-500">
                          Entry Validation
                        </p>

                        <p className="mt-2 font-medium">
                          {result.extracted_data.entry_validation ||
                            "Not detected"}
                        </p>
                      </div>

                      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                        <p className="text-xs text-slate-500">Stay Duration</p>

                        <p className="mt-2 font-medium">
                          {result.extracted_data.stay_duration ||
                            "Not detected"}
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* ================================================= */}
            {/* DOCUMENT VALIDATION */}
            {/* ================================================= */}

            {result.validation && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <h2 className="text-xl font-bold">Document Validation</h2>

                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Validation Status</p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.validation.status}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Validation Score</p>

                    <p className="mt-2 font-bold">
                      {result.validation.validation_score} / 100
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Risk Score</p>

                    <p className="mt-2 font-bold">
                      {result.validation.risk_score} / 100
                    </p>
                  </div>
                </div>

                <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">Recommendation</p>

                  <p className="mt-2 text-sm text-slate-300">
                    {result.validation.recommendation}
                  </p>
                </div>

                <div className="mt-5 space-y-3">
                  {result.validation.checks.map((check, index) => (
                    <div
                      key={index}
                      className="rounded-lg border border-slate-700 bg-slate-950 p-4"
                    >
                      <div className="flex items-center gap-2">
                        {check.status === "PASSED" ? (
                          <CheckCircle size={18} className="text-green-400" />
                        ) : check.status === "WARNING" ? (
                          <AlertTriangle
                            size={18}
                            className="text-yellow-400"
                          />
                        ) : (
                          <AlertTriangle size={18} className="text-red-400" />
                        )}

                        <p className="font-medium">{check.check}</p>

                        <span
                          className={`ml-auto text-xs font-bold ${
                            check.status === "PASSED"
                              ? "text-green-400"
                              : check.status === "WARNING"
                                ? "text-yellow-400"
                                : "text-red-400"
                          }`}
                        >
                          {check.status}
                        </span>
                      </div>

                      <p className="mt-1 text-sm text-slate-400">
                        {check.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Reference Verification */}
            {result.verification && (
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center gap-3">
                  <div className="rounded-xl bg-blue-100 p-3">
                    <FileSearch className="h-6 w-6 text-blue-600" />
                  </div>

                  <div>
                    <h2 className="text-xl font-bold text-slate-800">
                      Reference Verification
                    </h2>
                    <p className="text-sm text-slate-500">
                      Cross-check against the reference database
                    </p>
                  </div>
                </div>

                {result.verification.found ? (
                  <>
                    <div className="mb-5 flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 p-4">
                      <CheckCircle className="h-6 w-6 text-green-600" />

                      <div>
                        <p className="font-bold text-green-700">
                          REFERENCE FOUND
                        </p>

                        <p className="text-sm text-green-700">
                          A matching reference record was found in the database.
                        </p>
                      </div>
                    </div>

                    {result.verification.reference_data && (
                      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            NAME
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.full_name ||
                              "Not available"}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            DOCUMENT TYPE
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.document_type ||
                              "Not available"}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            DATE OF BIRTH
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.date_of_birth ||
                              "Not available"}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            NATIONALITY
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.nationality ||
                              "Not available"}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            EXPIRY DATE
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.expiry_date ||
                              "Not available"}
                          </p>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-semibold text-slate-500">
                            STATUS
                          </p>
                          <p className="mt-1 font-semibold text-slate-800">
                            {result.verification.reference_data.status ||
                              "Not available"}
                          </p>
                        </div>
                      </div>
                    )}
                    {result.verification.comparison && (
                      <div className="mt-6">
                        <h3 className="mb-4 text-lg font-bold text-slate-800">
                          Field-by-Field Comparison
                        </h3>

                        <div className="overflow-x-auto rounded-xl border border-slate-200">
                          <table className="w-full text-sm">
                            <thead className="bg-slate-50">
                              <tr>
                                <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                  Field
                                </th>

                                <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                  OCR Value
                                </th>

                                <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                  Reference Value
                                </th>

                                <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                  Status
                                </th>
                              </tr>
                            </thead>

                            <tbody>
                              {Object.entries(
                                result.verification.comparison,
                              ).map(([field, item]) => (
                                <tr
                                  key={field}
                                  className="border-t border-slate-200"
                                >
                                  <td className="px-4 py-3 font-medium text-slate-700">
                                    {item.label}
                                  </td>

                                  <td className="px-4 py-3 text-slate-600">
                                    {item.ocr_value || "—"}
                                  </td>

                                  <td className="px-4 py-3 text-slate-600">
                                    {item.reference_value || "—"}
                                  </td>

                                  <td className="px-4 py-3">
                                    {item.status === "MATCH" ? (
                                      <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">
                                        ✓ MATCH
                                      </span>
                                    ) : item.status === "MISMATCH" ? (
                                      <span className="inline-flex items-center rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-700">
                                        ⚠ MISMATCH
                                      </span>
                                    ) : item.status === "NOT DETECTED" ? (
                                      <span className="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-700">
                                        NOT DETECTED
                                      </span>
                                    ) : (
                                      <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                                        {item.status}
                                      </span>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="mt-0.5 h-6 w-6 text-amber-600" />

                      <div>
                        <p className="font-bold text-amber-700">
                          REFERENCE NOT FOUND
                        </p>

                        <p className="mt-1 text-sm text-amber-700">
                          No matching record was found in the current reference
                          database.
                        </p>

                        <p className="mt-2 text-xs text-amber-600">
                          This does not automatically mean the document is fake.
                          It means that a matching reference record was not
                          available for verification.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ================================================= */}
            {/* DISCREPANCY ANALYSIS */}
            {/* ================================================= */}

            {result.security_assessment?.discrepancy_analysis && (
              <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-5">
                <h3 className="mb-4 text-lg font-bold text-slate-800">
                  Discrepancy Analysis
                </h3>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className="rounded-xl bg-white p-4">
                    <p className="text-xs font-semibold text-slate-500">
                      DISCREPANCIES
                    </p>

                    <p className="mt-1 text-2xl font-bold text-slate-800">
                      {result.security_assessment.discrepancy_analysis.count}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white p-4">
                    <p className="text-xs font-semibold text-slate-500">
                      SEVERITY
                    </p>

                    <p className="mt-1 font-bold text-slate-800">
                      {result.security_assessment.discrepancy_analysis.severity}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white p-4">
                    <p className="text-xs font-semibold text-slate-500">
                      ANALYSIS
                    </p>

                    <p className="mt-1 text-sm text-slate-600">
                      {result.security_assessment.discrepancy_analysis.summary}
                    </p>
                  </div>
                </div>

                {result.security_assessment.discrepancy_analysis.items.length >
                  0 && (
                  <div className="mt-5 space-y-3">
                    {result.security_assessment.discrepancy_analysis.items.map(
                      (item, index) => (
                        <div
                          key={index}
                          className="rounded-xl border border-red-200 bg-red-50 p-4"
                        >
                          <p className="font-bold text-red-700">{item.field}</p>

                          <div className="mt-2 grid grid-cols-1 gap-3 md:grid-cols-2">
                            <div>
                              <p className="text-xs font-semibold text-slate-500">
                                OCR VALUE
                              </p>

                              <p className="mt-1 text-sm text-slate-700">
                                {item.ocr_value || "Not detected"}
                              </p>
                            </div>

                            <div>
                              <p className="text-xs font-semibold text-slate-500">
                                REFERENCE VALUE
                              </p>

                              <p className="mt-1 text-sm text-slate-700">
                                {item.reference_value || "Not available"}
                              </p>
                            </div>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                )}
              </div>
            )}
            {/* ================================================= */}
            {/* IMAGE & TAMPERING ANALYSIS */}
            {/* ================================================= */}

            {result.image_analysis && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <div className="flex items-center gap-3">
                  <ScanSearch size={26} className="text-blue-400" />

                  <h2 className="text-xl font-bold">
                    Image & Tampering Analysis
                  </h2>
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-4">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Image Quality</p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.image_analysis.image_quality}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Tampering Score</p>

                    <p className="mt-2 font-bold">
                      {result.image_analysis.tampering_score} / 100
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Tampering Status</p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.image_analysis.status}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Resolution</p>

                    <p className="mt-2 font-bold">
                      {result.image_analysis.resolution.width}
                      {" × "}
                      {result.image_analysis.resolution.height}
                    </p>
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  {result.image_analysis.checks.map((check, index) => (
                    <div
                      key={index}
                      className="rounded-lg border border-slate-700 bg-slate-950 p-4"
                    >
                      <div className="flex items-center gap-2">
                        <CheckCircle size={18} className="text-green-400" />

                        <p className="font-medium">{check.check}</p>

                        <span className="ml-auto text-xs font-bold text-green-400">
                          {check.status}
                        </span>
                      </div>

                      <p className="mt-1 text-sm text-slate-400">
                        {check.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}



                        {/* ================================================= */}
            {/* ADVANCED FORENSIC ANALYSIS */}
            {/* ================================================= */}

            {result.forensic_analysis && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <div className="flex items-center gap-3">
                  <ShieldCheck size={26} className="text-purple-400" />

                  <div>
                    <h2 className="text-xl font-bold">
                      Advanced Forensic Analysis
                    </h2>

                    <p className="text-sm text-slate-400">
                      Image-level forensic indicators for additional officer review.
                    </p>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-4">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Forensic Status
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.forensic_analysis.status}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Risk Level
                    </p>

                    <p className="mt-2 font-bold text-green-400">
                      {result.forensic_analysis.risk_level}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Forensic Risk Score
                    </p>

                    <p className="mt-2 font-bold">
                      {result.forensic_analysis.forensic_risk_score} / 100
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Image Format
                    </p>

                    <p className="mt-2 font-bold">
                      {result.forensic_analysis.metadata.format}
                    </p>
                  </div>
                </div>

                {/* FORENSIC METRICS */}

                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      ELA Score
                    </p>

                    <p className="mt-2 font-bold">
                      {result.forensic_analysis.ela.ela_score}
                    </p>

                    <p className="mt-1 text-sm text-slate-400">
                      High difference ratio:{" "}
                      {result.forensic_analysis.ela.high_difference_ratio}%
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Noise Variation
                    </p>

                    <p className="mt-2 font-bold">
                      {result.forensic_analysis.noise_analysis.noise_variation}
                    </p>

                    <p className="mt-1 text-sm text-slate-400">
                      {result.forensic_analysis.noise_analysis.suspicious
                        ? "Suspicious variation detected"
                        : "No strong inconsistency detected"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Sharpness
                    </p>

                    <p className="mt-2 font-bold">
                      {result.forensic_analysis.image_quality.sharpness}
                    </p>

                    <p className="mt-1 text-sm text-slate-400">
                      Brightness:{" "}
                      {result.forensic_analysis.image_quality.brightness}
                    </p>
                  </div>
                </div>

                {/* FORENSIC FINDINGS */}

                <div className="mt-5">
                  <p className="mb-3 text-sm font-semibold text-slate-300">
                    Forensic Findings
                  </p>

                  <div className="space-y-3">
                    {result.forensic_analysis.findings.map(
                      (finding, index) => (
                        <div
                          key={index}
                          className="rounded-lg border border-slate-700 bg-slate-950 p-4"
                        >
                          <div className="flex items-start gap-2">
                            <CheckCircle
                              size={18}
                              className="mt-0.5 text-green-400"
                            />

                            <p className="text-sm text-slate-300">
                              {finding}
                            </p>
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* FORENSIC DISCLAIMER */}

                <div className="mt-5 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-4">
                  <p className="text-sm text-yellow-400">
                    {result.forensic_analysis.message}
                  </p>
                </div>
              </div>
            )}

            {/* ================================================= */}
            {/* FACE DETECTION */}
            {/* ================================================= */}

            {result.face_analysis && (
              <div className="rounded-xl border border-slate-700 bg-slate-900 p-6">
                <div className="flex items-center gap-3">
                  <UserRound size={26} className="text-purple-400" />

                  <h2 className="text-xl font-bold">Face Detection Analysis</h2>
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-4">
                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Status</p>

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
                    <p className="text-xs text-slate-500">Faces Detected</p>

                    <p className="mt-2 font-bold">
                      {result.face_analysis.face_count}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Face Quality</p>

                    <p className="mt-2 font-bold">
                      {result.face_analysis.face_quality}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">Risk Level</p>

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
            {/* OFFICER REVIEW */}
            {/* ================================================= */}

            <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-6">
              <h2 className="text-xl font-bold text-blue-400">
                Officer Review
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Review the preliminary AI screening results before making an
                authorized decision.
              </p>

              <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">Screening Result</p>

                <p
                  className={`mt-2 font-bold ${
                    officerScreeningStatus === "REVIEW REQUIRED"
                      ? "text-yellow-400"
                      : officerScreeningStatus === "VERIFIED"
                        ? "text-green-400"
                        : "text-red-400"
                  }`}
                >
                  {officerScreeningStatus}
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  Risk Level: {officerRiskLevel}
                </p>

                <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950 p-4">
  <p className="text-xs text-slate-500">
    Officer Review Status
  </p>

  <p
    className={`mt-2 font-bold ${
      officerReviewStatus === "REVIEWED"
        ? "text-green-400"
        : officerReviewStatus === "FLAGGED"
        ? "text-red-400"
        : "text-yellow-400"
    }`}
  >
    {officerReviewStatus}
  </p>
</div>

                {faceMismatch && (
                  <div className="mt-4 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-4">
                    <p className="text-sm font-semibold text-yellow-400">
                      ⚠ Face verification mismatch detected.
                    </p>

                    <p className="mt-1 text-sm text-slate-400">
                      The traveller's face does not match the face associated
                      with the presented document or reference record. Manual
                      officer review is required.
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-5">
                <label className="text-sm font-medium text-slate-300">
                  Officer Notes
                </label>

                <textarea
                  className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-slate-200 outline-none focus:border-blue-500"
                  rows={4}
                  placeholder="Enter review notes..."
                  value={officerNotes}
                  onChange={(event) => {
                    setOfficerNotes(event.target.value);
                  }}
                />
              </div>

              <div className="mt-5 flex flex-wrap items-center gap-3">
                <p className="text-sm text-slate-300">
                  Review status: {" "}
                  <span className="font-semibold text-blue-400">
                    {officerReviewStatus}
                  </span>
                </p>

                <button
                  type="button"
                  className="rounded-lg bg-green-600 px-5 py-2 text-sm font-semibold text-white hover:bg-green-500"
                 onClick={async () => {
  if (!result?.screening_id) {
    alert("Screening ID not available.");
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/verification/screening-history/${result.screening_id}/review?review_status=REVIEWED&officer_notes=${encodeURIComponent(
        officerNotes
      )}`,
      {
        method: "PUT",
      }
    );

    const data = await response.json();

    if (!data.success) {
      alert(data.message || "Failed to save officer review.");
      return;
    }

    setOfficerReviewStatus("REVIEWED");

    alert("Document marked as reviewed and saved to PostgreSQL.");
  } catch (error) {
    console.error("Failed to save officer review:", error);
    alert("Unable to save officer review.");
  }
}}
                >
                  ✓ Mark as Reviewed
                </button>

                <button
                  type="button"
                  className="rounded-lg border border-yellow-500/40 bg-yellow-500/10 px-5 py-2 text-sm font-semibold text-yellow-400 hover:bg-yellow-500/20"
                  onClick={() => {
                    setOfficerReviewStatus("FLAGGED");
                    alert("Document flagged for additional review.");
                  }}
                >
                  ⚠ Flag for Review
                </button>
              </div>
            </div>

            {/* ================================================= */}
            {/* SUCCESS MESSAGE */}
            {/* ================================================= */}

            <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4 text-center">
              <p className="text-sm text-green-400">✓ {result.message}</p>
            </div>
          </div>
        )}
      </div>
  );
}
