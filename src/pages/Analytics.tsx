import {
  BarChart3,
  CheckCircle,
  Clock,
  AlertTriangle,
  FileSearch,
  ArrowLeft,
  ShieldCheck,
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

export default function Analytics() {
  const history: ScreeningRecord[] = JSON.parse(
    localStorage.getItem("borderguard_history") || "[]"
  );

  const totalScreenings = history.length;

  const verifiedCount = history.filter(
    (item) => item.status === "VERIFIED"
  ).length;

  const reviewCount = history.filter(
    (item) => item.status === "REVIEW"
  ).length;

  const highRiskCount = history.filter((item) => {
    const risk = item.riskScore ?? item.risk_score ?? 0;

    return (
      risk >= 80 ||
      item.status === "HIGH RISK"
    );
  }).length;

  const verificationRate =
    totalScreenings > 0
      ? Math.round(
          (verifiedCount / totalScreenings) * 100
        )
      : 0;

  const reviewRate =
    totalScreenings > 0
      ? Math.round(
          (reviewCount / totalScreenings) * 100
        )
      : 0;

  const highRiskRate =
    totalScreenings > 0
      ? Math.round(
          (highRiskCount / totalScreenings) * 100
        )
      : 0;

  const documentTypes = history.reduce(
    (acc: Record<string, number>, item) => {
      const type =
        item.documentType ||
        item.document_type ||
        "Unknown";

      acc[type] = (acc[type] || 0) + 1;

      return acc;
    },
    {}
  );

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* HEADER */}

      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400">
              <BarChart3 size={26} />
            </div>

            <div>

              <h1 className="text-2xl font-bold">
                Analytics
              </h1>

              <p className="text-sm text-slate-400">
                Monitor BorderGuard AI screening statistics.
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

        {/* PAGE TITLE */}

        <div className="mb-8">

          <h2 className="text-2xl font-bold">
            Screening Analytics
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Overview of documents processed by BorderGuard AI.
          </p>

        </div>


        {/* STAT CARDS */}

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">

          {/* TOTAL */}

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <div className="flex items-center justify-between">

              <p className="text-sm text-slate-400">
                Total Screenings
              </p>

              <div className="rounded-lg bg-blue-500/10 p-2 text-blue-400">
                <FileSearch size={20} />
              </div>

            </div>

            <p className="mt-4 text-3xl font-bold">
              {totalScreenings}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Documents processed
            </p>

          </div>


          {/* VERIFIED */}

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <div className="flex items-center justify-between">

              <p className="text-sm text-slate-400">
                Verified
              </p>

              <div className="rounded-lg bg-emerald-500/10 p-2 text-emerald-400">
                <CheckCircle size={20} />
              </div>

            </div>

            <p className="mt-4 text-3xl font-bold text-emerald-400">
              {verifiedCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {verificationRate}% verification rate
            </p>

          </div>


          {/* REVIEW */}

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <div className="flex items-center justify-between">

              <p className="text-sm text-slate-400">
                Under Review
              </p>

              <div className="rounded-lg bg-yellow-500/10 p-2 text-yellow-400">
                <Clock size={20} />
              </div>

            </div>

            <p className="mt-4 text-3xl font-bold text-yellow-400">
              {reviewCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {reviewRate}% of screenings
            </p>

          </div>


          {/* HIGH RISK */}

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

            <div className="flex items-center justify-between">

              <p className="text-sm text-slate-400">
                High Risk
              </p>

              <div className="rounded-lg bg-red-500/10 p-2 text-red-400">
                <AlertTriangle size={20} />
              </div>

            </div>

            <p className="mt-4 text-3xl font-bold text-red-400">
              {highRiskCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {highRiskRate}% of screenings
            </p>

          </div>

        </div>


        {/* PERFORMANCE */}

        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <ShieldCheck
              size={22}
              className="text-blue-400"
            />

            <div>

              <h2 className="font-semibold">
                Screening Performance
              </h2>

              <p className="text-sm text-slate-500">
                Current screening outcome distribution.
              </p>

            </div>

          </div>


          <div className="mt-6 space-y-6">

            {/* VERIFIED BAR */}

            <div>

              <div className="mb-2 flex justify-between text-sm">

                <span className="text-slate-300">
                  Verified
                </span>

                <span className="text-emerald-400">
                  {verificationRate}%
                </span>

              </div>

              <div className="h-3 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-emerald-500"
                  style={{
                    width: `${verificationRate}%`,
                  }}
                />

              </div>

            </div>


            {/* REVIEW BAR */}

            <div>

              <div className="mb-2 flex justify-between text-sm">

                <span className="text-slate-300">
                  Under Review
                </span>

                <span className="text-yellow-400">
                  {reviewRate}%
                </span>

              </div>

              <div className="h-3 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-yellow-500"
                  style={{
                    width: `${reviewRate}%`,
                  }}
                />

              </div>

            </div>


            {/* HIGH RISK BAR */}

            <div>

              <div className="mb-2 flex justify-between text-sm">

                <span className="text-slate-300">
                  High Risk
                </span>

                <span className="text-red-400">
                  {highRiskRate}%
                </span>

              </div>

              <div className="h-3 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-red-500"
                  style={{
                    width: `${highRiskRate}%`,
                  }}
                />

              </div>

            </div>

          </div>

        </div>


        {/* DOCUMENT TYPES */}

        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <FileSearch
              size={22}
              className="text-blue-400"
            />

            <div>

              <h2 className="font-semibold">
                Document Type Distribution
              </h2>

              <p className="text-sm text-slate-500">
                Number of documents processed by type.
              </p>

            </div>

          </div>


          {Object.keys(documentTypes).length === 0 ? (

            <div className="mt-6 rounded-lg border border-slate-700 bg-slate-950 p-8 text-center">

              <p className="text-sm text-slate-500">
                No screening data available yet.
              </p>

            </div>

          ) : (

            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">

              {Object.entries(documentTypes).map(
                ([type, count]) => (

                  <div
                    key={type}
                    className="rounded-lg border border-slate-700 bg-slate-950 p-5"
                  >

                    <p className="text-sm text-slate-400">
                      {type}
                    </p>

                    <p className="mt-2 text-2xl font-bold text-blue-400">
                      {count}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      document{count !== 1 ? "s" : ""}
                    </p>

                  </div>

                )
              )}

            </div>

          )}

        </div>


        {/* FOOTER INFO */}

        <div className="mt-6 rounded-xl border border-blue-500/20 bg-blue-500/5 p-5">

          <div className="flex items-start gap-3">

            <BarChart3
              size={20}
              className="mt-0.5 text-blue-400"
            />

            <div>

              <p className="font-medium text-blue-400">
                Analytics powered by screening history
              </p>

              <p className="mt-1 text-sm text-slate-400">
                Statistics are automatically calculated from
                documents processed by the BorderGuard AI
                screening system.
              </p>

            </div>

          </div>

        </div>

      </main>

    </div>
  );
}