import {
  AlertTriangle,
  ShieldCheck,
  FileSearch,
  ArrowLeft,
} from "lucide-react";

import { Link } from "react-router-dom";

type ScreeningRecord = {
  id?: string;
  name?: string;
  applicant?: string;
  documentType?: string;
  document_type?: string;
  riskScore?: number;
  risk_score?: number;
  riskLevel?: string;
  status?: string;
  date?: string;
};

export default function SecurityAlerts() {
  const history: ScreeningRecord[] = JSON.parse(
    localStorage.getItem("borderguard_history") || "[]"
  );

  const alerts = history.filter((item) => {
    const risk = item.riskScore ?? item.risk_score ?? 0;

    return (
      risk >= 40 ||
      item.status === "REVIEW" ||
      item.status === "HIGH RISK"
    );
  });

  const highRiskCount = history.filter((item) => {
    const risk = item.riskScore ?? item.risk_score ?? 0;

    return risk >= 80 || item.status === "HIGH RISK";
  }).length;

  const reviewCount = history.filter((item) => {
    const risk = item.riskScore ?? item.risk_score ?? 0;

    return (
      (risk >= 40 && risk < 80) ||
      item.status === "REVIEW"
    );
  }).length;

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* HEADER */}

      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-red-500/10 p-3 text-red-400">
              <AlertTriangle size={24} />
            </div>

            <div>

              <h1 className="text-2xl font-bold">
                Security Alerts
              </h1>

              <p className="text-sm text-slate-400">
                Monitor documents requiring security attention.
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

      <main className="mx-auto max-w-6xl p-8">

        {/* SUMMARY CARDS */}

        <div className="grid gap-5 md:grid-cols-3">

          <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-5">

            <p className="text-sm text-slate-400">
              High Risk Alerts
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {highRiskCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Immediate attention required
            </p>

          </div>


          <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-5">

            <p className="text-sm text-slate-400">
              Documents Under Review
            </p>

            <p className="mt-2 text-3xl font-bold text-yellow-400">
              {reviewCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Requires officer review
            </p>

          </div>


          <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-5">

            <p className="text-sm text-slate-400">
              Total Security Alerts
            </p>

            <p className="mt-2 text-3xl font-bold text-blue-400">
              {alerts.length}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Active screening alerts
            </p>

          </div>

        </div>


        {/* ALERT LIST */}

        <div className="mt-8 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

          <div className="border-b border-slate-800 p-6">

            <h2 className="font-semibold">
              Active Security Alerts
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Documents flagged by the automated screening system.
            </p>

          </div>


          {alerts.length === 0 ? (

            <div className="flex flex-col items-center justify-center p-12 text-center">

              <div className="rounded-full bg-emerald-500/10 p-4 text-emerald-400">
                <ShieldCheck size={32} />
              </div>

              <h3 className="mt-4 text-lg font-semibold">
                No Security Alerts
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                All processed documents are currently within acceptable risk levels.
              </p>

            </div>

          ) : (

            <div className="divide-y divide-slate-800">

              {alerts
                .slice()
                .reverse()
                .map((item, index) => {

                  const risk =
                    item.riskScore ??
                    item.risk_score ??
                    0;

                  const isHighRisk =
                    risk >= 80 ||
                    item.status === "HIGH RISK";

                  return (
                    <div
                      key={index}
                      className="p-6 transition hover:bg-slate-800/40"
                    >

                      <div className="flex items-start justify-between gap-5">

                        <div className="flex items-start gap-4">

                          <div
                            className={`rounded-lg p-3 ${
                              isHighRisk
                                ? "bg-red-500/10 text-red-400"
                                : "bg-yellow-500/10 text-yellow-400"
                            }`}
                          >
                            <AlertTriangle size={22} />
                          </div>


                          <div>

                            <p className="font-semibold">
                              {item.name ||
                                item.applicant ||
                                "Unknown Applicant"}
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                              {item.documentType ||
                                item.document_type ||
                                "Unknown Document"}
                            </p>

                          </div>

                        </div>


                        <span
                          className={`rounded-full px-3 py-1 text-xs font-bold ${
                            isHighRisk
                              ? "bg-red-500/10 text-red-400"
                              : "bg-yellow-500/10 text-yellow-400"
                          }`}
                        >
                          {isHighRisk
                            ? "HIGH RISK"
                            : "REVIEW"}
                        </span>

                      </div>


                      <div className="mt-5 grid gap-4 md:grid-cols-3">

                        <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                          <p className="text-xs text-slate-500">
                            Screening ID
                          </p>

                          <p className="mt-1 text-sm font-medium">
                            {item.id || `#BG-${10232 - index}`}
                          </p>

                        </div>


                        <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                          <p className="text-xs text-slate-500">
                            Risk Score
                          </p>

                          <p
                            className={`mt-1 text-sm font-bold ${
                              isHighRisk
                                ? "text-red-400"
                                : "text-yellow-400"
                            }`}
                          >
                            {risk} / 100
                          </p>

                        </div>


                        <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">

                          <p className="text-xs text-slate-500">
                            Status
                          </p>

                          <p className="mt-1 text-sm font-bold">
                            {item.status ||
                              (isHighRisk
                                ? "HIGH RISK"
                                : "REVIEW")}
                          </p>

                        </div>

                      </div>

                    </div>
                  );
                })}

            </div>

          )}

        </div>


        {/* INFORMATION */}

        <div className="mt-6 flex items-start gap-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-5">

          <FileSearch
            size={20}
            className="mt-0.5 text-blue-400"
          />

          <div>

            <p className="font-medium text-blue-400">
              Automated Security Monitoring
            </p>

            <p className="mt-1 text-sm text-slate-400">
              BorderGuard AI automatically identifies documents
              that require additional officer review based on
              screening risk scores.
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}