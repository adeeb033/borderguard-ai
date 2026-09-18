import {
  History,
  ShieldCheck,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Clock,
} from "lucide-react";

import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

type ScreeningRecord = {
  id: string;
  filename: string;
  name?: string;
  documentType: string;
  riskScore: number;
  riskLevel: string;
  status: string;
  reviewStatus?: string;
  officerNotes?: string;
  reviewedAt?: string;
  ocrConfidence?: number | string;
  validationScore?: number | string;
  tamperingScore?: number | string;
  faceDetected?: boolean;
  riskReasons?: string[];
  date: string;
};

export default function ScreeningHistory() {
  const [records, setRecords] = useState<ScreeningRecord[]>([]);

useEffect(() => {
  fetch("http://127.0.0.1:8000/verification/screening-history")
    .then((response) => response.json())
    .then((data) => {
      if (data.history) {
        const mappedRecords: ScreeningRecord[] = data.history.map(
          (item: any) => ({
            id: String(item.screening_id),
            filename: item.filename || "",
            name: item.applicant_name || "",
            documentType: item.document_type || "",
            riskScore: Number(item.risk_score || 0),
            riskLevel: item.risk_level || "",
            status: item.status || "",
            reviewStatus: item.review_status || "PENDING",
            officerNotes: item.officer_notes || "",
            reviewedAt: item.reviewed_at || "",
            ocrConfidence: item.ocr_confidence ?? 0,
            validationScore: item.validation_score ?? 0,
            tamperingScore: item.tampering_score ?? 0,
            faceDetected: item.face_detected ?? false,
            riskReasons: item.risk_reasons || [],
            date: item.screening_date || "",
          })
        );

        setRecords(mappedRecords);
      }
    })
    .catch((error) => {
      console.error("Failed to load screening history:", error);
    });
}, []);
  const [selectedRecord, setSelectedRecord] =
    useState<ScreeningRecord | null>(null);
  const [reviewStatus, setReviewStatus] =
    useState("PENDING");

  const [officerNotes, setOfficerNotes] =
    useState("");
  const getRiskStyle = (score: number) => {
    if (score >= 80) {
      return "text-red-400";
    }

    if (score >= 40) {
      return "text-yellow-400";
    }

    return "text-emerald-400";
  };

  const getStatusStyle = (status: string) => {
    if (status === "VERIFIED") {
      return "bg-emerald-500/10 text-emerald-400";
    }

    if (status === "REVIEW") {
      return "bg-yellow-500/10 text-yellow-400";
    }
    if (status === "REVIEWED") {
      return "bg-blue-500/10 text-blue-400";
    }

    return "bg-red-500/10 text-red-400";
  };

  const getStatusIcon = (status: string) => {
    if (status === "VERIFIED") {
      return <CheckCircle size={16} />;
    }

    if (status === "REVIEW") {
      return <Clock size={16} />;
    }
    if (status === "REVIEWED") {
      return <CheckCircle size={16} />;
    }

    return <AlertTriangle size={16} />;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">

          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">

            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">
                  Screening Details
                </h2>

                <p className="mt-1 text-sm text-slate-400">
                  BorderGuard AI preliminary screening report
                </p>
              </div>

              <button
                type="button"
                className="rounded-lg px-3 py-2 text-slate-400 hover:bg-slate-800 hover:text-white"
                onClick={() => {
                  setSelectedRecord(null);
                }}
              >
                ✕
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">

              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Document Type
                </p>

                <p className="mt-1 font-semibold text-white">
                  {selectedRecord.documentType}
                </p>
              </div>

              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Applicant
                </p>

                <p className="mt-1 font-semibold text-white">
                  {selectedRecord.name}
                </p>
              </div>

              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Risk Score
                </p>

                <p className={`mt-1 text-xl font-bold ${getRiskStyle(
                  selectedRecord.riskScore
                )}`}>
                  {selectedRecord.riskScore}%
                </p>
              </div>

              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Risk Level
                </p>

                <p className="mt-1 font-semibold text-white">
                  {selectedRecord.riskLevel}
                </p>
              </div>

              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4 md:col-span-2">
                <p className="text-xs text-slate-500">
                  Screening Status
                </p>

                <p className="mt-1 font-semibold text-blue-400">
                  {selectedRecord.reviewStatus === "REVIEWED"
                    ? "REVIEWED"
                    : selectedRecord.status}
                </p>
              </div>
              <div className="mt-6 rounded-xl border border-blue-500/20 bg-blue-500/5 p-5">
                <h3 className="text-lg font-bold text-blue-400">
                  AI Screening Evidence
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  Preliminary signals generated during document screening
                </p>

                <div className="mt-4 grid gap-4 md:grid-cols-2">

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      OCR Confidence
                    </p>

                    <p className="mt-1 font-semibold text-white">
                      {selectedRecord.ocrConfidence ?? "N/A"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Validation Score
                    </p>

                    <p className="mt-1 font-semibold text-white">
                      {selectedRecord.validationScore ?? "N/A"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Tampering Score
                    </p>

                    <p className="mt-1 font-semibold text-white">
                      {selectedRecord.tamperingScore ?? "N/A"}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <p className="text-xs text-slate-500">
                      Face Detection
                    </p>

                    <p className="mt-1 font-semibold text-white">
                      {selectedRecord.faceDetected === true
                        ? "Detected"
                        : selectedRecord.faceDetected === false
                        ? "Not Detected"
                        : "N/A"}
                    </p>
                  </div>

                </div>

                {selectedRecord.riskReasons &&
                  selectedRecord.riskReasons.length > 0 && (
                    <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950 p-4">

                      <p className="text-sm font-semibold text-blue-400">
                        Why this decision?
                      </p>

                      <div className="mt-3 space-y-2">
                        {selectedRecord.riskReasons.map(
                          (reason: string, index: number) => (
                            <p
                              key={index}
                              className="text-sm text-slate-300"
                            >
                              ✓ {reason}
                            </p>
                          )
                        )}
                      </div>

                    </div>
                  )}
              </div>

            </div>

            <div className="mt-4 rounded-lg border border-blue-500/30 bg-slate-950 p-4">
              <p className="text-sm font-semibold text-blue-400">
                Officer Review
              </p>

              <div className="mt-3 rounded-lg border border-slate-700 bg-slate-900 p-3">
                <p className="text-xs text-slate-500">
                  Officer Decision
                </p>

                <p
                  className={`mt-1 text-sm font-semibold ${
                    reviewStatus === "APPROVED"
                      ? "text-emerald-400"
                      : reviewStatus === "REJECTED"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                >
                  {reviewStatus}
                </p>
              </div>

              <div className="mt-4">
                <label className="text-xs font-medium text-slate-400">
                  Review Status
                </label>

                <select
                  value={reviewStatus}
                  onChange={(event) => setReviewStatus(event.target.value)}
                  className="mt-2 w-full rounded-lg border border-blue-500/40 bg-slate-900 px-3 py-2.5 text-sm font-medium text-white outline-none focus:border-blue-500"
                >
                  <option value="PENDING">🟡 Pending</option>
                  <option value="APPROVED">🟢 Approved</option>
                  <option value="REJECTED">🔴 Rejected</option>
                </select>
              </div>

              <div className="mt-4">
                <label className="text-xs text-slate-500">
                  Officer Notes
                </label>

                <textarea
                  value={officerNotes}
                  onChange={(event) => setOfficerNotes(event.target.value)}
                  placeholder="Enter officer review notes..."
                  rows={4}
                  className="mt-2 w-full resize-none rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-blue-500"
                />
              </div>

              <button
                type="button"
                className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
               onClick={async () => {
  if (!selectedRecord) return;

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/verification/screening-history/${selectedRecord.id}/review?review_status=${encodeURIComponent(
        reviewStatus
      )}&officer_notes=${encodeURIComponent(officerNotes)}`,
      {
        method: "PUT",
      }
    );

    const data = await response.json();

    if (!data.success) {
      console.error("Failed to save officer review:", data.message);
      return;
    }

    const updatedRecord: ScreeningRecord = {
      ...selectedRecord,
      reviewStatus: data.record.review_status,
      officerNotes: data.record.officer_notes || "",
      reviewedAt: data.record.reviewed_at || "",
      status: data.record.status,
    };

    setRecords((currentRecords) =>
      currentRecords.map((record) =>
        record.id === updatedRecord.id
          ? updatedRecord
          : record
      )
    );

    setSelectedRecord(updatedRecord);
    setReviewStatus(data.record.review_status);

    console.log("Officer review saved to PostgreSQL");
  } catch (error) {
    console.error("Failed to save officer review:", error);
  }
}}
              >
                Save Review
              </button>
            </div>

            {selectedRecord.reviewedAt && (
              <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Reviewed At
                </p>

                <p className="mt-1 text-sm text-slate-300">
                  {selectedRecord.reviewedAt}
                </p>
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-500"
                onClick={() => {
                  setSelectedRecord(null);
                }}
              >
                Close
              </button>
            </div>

          </div>

        </div>
      )}

      {/* HEADER */}

      <header className="border-b border-slate-800 bg-slate-900">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-600 p-3">
              <ShieldCheck size={22} />
            </div>

            <div>

              <h1 className="font-bold">
                BorderGuard AI
              </h1>

              <p className="text-xs text-slate-500">
                AI Document Screening Platform
              </p>

            </div>

          </div>

          <Link
            to="/"
            className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
          >
            <ArrowLeft size={16} />
            Dashboard
          </Link>

        </div>

      </header>


      {/* MAIN */}

      <main className="mx-auto max-w-7xl p-8">

        {/* TITLE */}

        <div className="mb-8">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400">
              <History size={26} />
            </div>

            <div>

              <h2 className="text-3xl font-bold">
                Screening History
              </h2>

              <p className="mt-1 text-slate-400">
                Review documents previously processed by BorderGuard AI.
              </p>

            </div>

          </div>

        </div>


        {/* SUMMARY */}

        <div className="mb-6 grid gap-5 md:grid-cols-3">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-500">
              Total Screenings
            </p>

            <p className="mt-2 text-3xl font-bold">
              {records.length}
            </p>

          </div>


          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-500">
              Verified
            </p>

            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {
                records.filter(
                  (record) => record.status === "VERIFIED"
                ).length
              }
            </p>

          </div>


          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-500">
              High Risk
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {
                records.filter(
                  (record) => record.status === "HIGH RISK"
                ).length
              }
            </p>

          </div>

        </div>


        {/* HISTORY TABLE */}

        <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

          {/* TABLE HEADER */}

          <div className="border-b border-slate-800 p-6">

            <h3 className="font-semibold">
              Previous Screenings
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Documents processed by the screening system.
            </p>

          </div>


          {/* COLUMN HEADER */}

          <div className="hidden grid-cols-6 border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-wider text-slate-500 md:grid">

            <span>ID</span>

            <span>Document</span>

            <span>Type</span>

            <span>Risk</span>

            <span>Status</span>

            <span>Date</span>

          </div>


          {/* RECORDS */}

          <div className="divide-y divide-slate-800">

            {records.map((record) => (

              <div
                key={record.id}
                className="grid grid-cols-1 gap-3 px-6 py-5 transition hover:bg-slate-800/40 md:grid-cols-6 md:items-center"
              >

                {/* ID */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    ID
                  </p>

                  <p className="text-sm font-medium">
                    {record.id}
                  </p>

                </div>


                {/* DOCUMENT */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    Document
                  </p>

                  <p className="text-sm font-medium">
                    {record.filename}
                  </p>

                </div>


                {/* TYPE */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    Type
                  </p>

                  <p className="text-sm text-slate-300">
                    {record.documentType}
                  </p>

                </div>


                {/* RISK */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    Risk
                  </p>

                  <p
                    className={`font-semibold ${getRiskStyle(
                      record.riskScore
                    )}`}
                  >
                    {record.riskScore}%
                  </p>

                  <p className="text-xs text-slate-500">
                    {record.riskLevel}
                  </p>

                </div>


                {/* STATUS */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    Status
                  </p>

                  <span
                    className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${getStatusStyle(
                      record.status
                    )}`}
                  >
                    {getStatusIcon(record.status)}

                    {record.status}
                  </span>

                  {record.reviewStatus &&
                    record.reviewStatus !== "PENDING" && (
                      <p className="mt-1 text-xs font-medium text-slate-400">
                        Officer:{" "}
                        <span
                          className={
                            record.reviewStatus === "APPROVED"
                              ? "text-emerald-400"
                              : "text-red-400"
                          }
                        >
                          {record.reviewStatus}
                        </span>
                      </p>
                    )}

                </div>
                <button
                  type="button"
                  className="mt-2 rounded-lg border border-blue-500/40 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400 hover:bg-blue-500/20"
                  onClick={() => {
                    setSelectedRecord(record);

                    setReviewStatus(
                      record.reviewStatus || "PENDING"
                    );

                    setOfficerNotes(record.officerNotes || "");
                  }}
                >
                  View Details
                </button>


                {/* DATE */}

                <div>

                  <p className="text-xs text-slate-500 md:hidden">
                    Date
                  </p>

                  <p className="text-sm text-slate-400">
                    {record.date}
                  </p>

                </div>

              </div>

            ))}

          </div>

        </div>

      </main>

    </div>
  );
}