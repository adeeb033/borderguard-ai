import {
  History,
  ShieldCheck,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Clock,
} from "lucide-react";

import { Link } from "react-router-dom";

type ScreeningRecord = {
  id: string;
  filename: string;
  documentType: string;
  riskScore: number;
  riskLevel: string;
  status: string;
  date: string;
};

export default function ScreeningHistory() {
  const records: ScreeningRecord[] = JSON.parse(
  localStorage.getItem("borderguard_history") || "[]"
);
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

    return "bg-red-500/10 text-red-400";
  };

  const getStatusIcon = (status: string) => {
    if (status === "VERIFIED") {
      return <CheckCircle size={16} />;
    }

    if (status === "REVIEW") {
      return <Clock size={16} />;
    }

    return <AlertTriangle size={16} />;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">

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

                </div>


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