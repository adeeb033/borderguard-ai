import {
  LayoutDashboard,
  FileSearch,
  History,
  Bell,
  BarChart3,
  ShieldCheck,
  Upload,
  CheckCircle,
  Clock,
  AlertTriangle,
  Activity,
  LockKeyhole,
  UserRound,
  ChevronRight,
} from "lucide-react";

import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
  Navigate,
} from "react-router-dom";

import { useEffect, useState, type ReactNode } from "react";

import NewScreening from "./pages/NewScreening";
import ScreeningHistory from "./pages/ScreeningHistory";
import SecurityAlerts from "./pages/SecurityAlerts";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
/* =====================================================
   MAIN APP
===================================================== */

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("borderguard_authenticated") === "true"
  );

  const handleLogin = () => {
    localStorage.setItem(
      "borderguard_authenticated",
      "true"
    );

    setIsAuthenticated(true);
  };

  return (
    <BrowserRouter>
      <Routes>

        {/* Login */}
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />

        {/* Dashboard */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Dashboard />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* New Screening */}
        <Route
          path="/screening"
          element={
            isAuthenticated ? (
              <NewScreening />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Screening History */}
        <Route
          path="/history"
          element={
            isAuthenticated ? (
              <ScreeningHistory />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Security Alerts */}
        <Route
          path="/alerts"
          element={
            isAuthenticated ? (
              <SecurityAlerts />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Analytics */}
        <Route
          path="/analytics"
          element={
            isAuthenticated ? (
              <Analytics />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

      </Routes>
    </BrowserRouter>
  );
}
/* =====================================================
   DASHBOARD
===================================================== */

function Dashboard() {


   const [gateData, setGateData] = useState<{
  total_gates: number;
  active_gates: number;
  inactive_gates: number;
  gates: {
    id: number;
    gate_code: string;
    status: string;
    created_at: string;
  }[];
}>({
  total_gates: 0,
  active_gates: 0,
  inactive_gates: 0,
  gates: [],
});

useEffect(() => {
  fetch("http://127.0.0.1:8000/verification/gates")
    .then((response) => response.json())
    .then((data) => {
      setGateData(data);
    })
    .catch((error) => {
      console.error("Failed to load gate status:", error);
    });
}, []);

const totalGates = gateData.total_gates;
const activeGates = gateData.active_gates;
const gates = gateData.gates;

  const [history, setHistory] = useState<any[]>([]);

useEffect(() => {
  fetch("http://127.0.0.1:8000/verification/screening-history")
    .then((response) => response.json())
    .then((data) => {
      if (data.history) {
        const mappedHistory = data.history.map((item: any) => ({
          id: item.screening_id,
          name: item.applicant_name || "",
          applicant: item.applicant_name || "",
          documentType: item.document_type || "",
          document_type: item.document_type || "",
          riskScore: Number(item.risk_score || 0),
          risk_score: Number(item.risk_score || 0),
          riskLevel: item.risk_level || "",
          status: item.status || "",
          date: item.screening_date || "",
        }));

        setHistory(mappedHistory);
      }
    })
    .catch((error) => {
      console.error(
        "Failed to load dashboard screening history:",
        error
      );
    });
}, []);

const totalScreenings = history.length;

const verifiedCount = history.filter(
  (item: any) => item.status === "VERIFIED"
).length;

const reviewCount = history.filter(
  (item: any) =>
    item.status === "REVIEW" ||
    item.status === "REVIEWED"
).length;

const highRiskCount = history.filter(
  (item: any) =>
    item.riskLevel === "HIGH" ||
    item.status === "HIGH RISK"
).length;

const verificationRate =
  totalScreenings > 0
    ? ((verifiedCount / totalScreenings) * 100).toFixed(1)
    : "0.0";

const reviewRate =
  totalScreenings > 0
    ? ((reviewCount / totalScreenings) * 100).toFixed(1)
    : "0.0";

const highRiskRate =
  totalScreenings > 0
    ? ((highRiskCount / totalScreenings) * 100).toFixed(1)
    : "0.0";
  return (
    <div
  className="min-h-screen text-white"
  style={{
    backgroundColor: "#05070a",
    backgroundImage: `
      linear-gradient(rgba(0, 255, 170, 0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 255, 170, 0.035) 1px, transparent 1px),
      radial-gradient(circle at 20% 20%, rgba(0, 120, 255, 0.10), transparent 35%),
      radial-gradient(circle at 80% 80%, rgba(0, 255, 170, 0.06), transparent 35%)
    `,
    backgroundSize: "40px 40px, 40px 40px, 100% 100%, 100% 100%",
    backgroundAttachment: "fixed",
  }}
>

      {/* =================================================
          SIDEBAR
      ================================================= */}

     <aside className="fixed left-0 top-0 h-screen w-64 border-r border-slate-800/80 bg-[#070a0d] font-mono shadow-2xl">

  {/* LOGO / SYSTEM IDENTITY */}

  <div className="border-b border-slate-800/80 p-5">

    <div className="flex items-center gap-3">

      <div className="rounded-lg border border-blue-500/40 bg-blue-500/10 p-3 text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.15)]">
        <ShieldCheck size={22} />
      </div>

      <div>
        <h1 className="font-bold tracking-wide text-white">
          BorderGuard AI
        </h1>

        <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-slate-500">
          Security Console
        </p>
      </div>

    </div>

  </div>


  {/* NAVIGATION */}

  <div className="px-4 pt-5">

    <p className="mb-3 px-2 text-[10px] uppercase tracking-[0.2em] text-slate-600">
      System Navigation
    </p>

    <nav className="space-y-1">

      <NavItem
        to="/"
        icon={<LayoutDashboard size={18} />}
        text="Dashboard"
      />

      <NavItem
        to="/screening"
        icon={<FileSearch size={18} />}
        text="New Screening"
      />

      <NavItem
        to="/history"
        icon={<History size={18} />}
        text="Screening History"
      />

      <NavItem
        to="/alerts"
        icon={<Bell size={18} />}
        text="Security Alerts"
      />

      <NavItem
        to="/analytics"
        icon={<BarChart3 size={18} />}
        text="Analytics"
      />

    </nav>

  </div>


  {/* SYSTEM STATUS */}

  <div className="absolute bottom-0 w-full border-t border-slate-800/80 bg-[#05080b] p-5">

    <p className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
      System Status
    </p>

    <div className="mt-3 flex items-center gap-3">

      <span className="relative flex h-2.5 w-2.5">

        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-30" />

        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-green-500" />

      </span>

      <span className="text-xs font-semibold uppercase tracking-wider text-green-400">
        System Online
      </span>

    </div>

    <p className="mt-2 text-[9px] text-slate-600">
      AI SCREENING ENGINE READY
    </p>

  </div>

</aside>


      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <main className="ml-64">

        {/* HEADER */}

        <header className="flex items-center justify-between border-b border-slate-800 px-8 py-6">

          <div>

            <div className="flex items-center gap-2">

              <LockKeyhole
                size={18}
                className="text-blue-400"
              />

              <h2 className="text-xl font-bold">
                Border Security Dashboard
              </h2>

            </div>

            <p className="mt-1 text-sm text-slate-400">
              AI-powered document screening platform
            </p>

          </div>


          {/* OFFICER */}

          <div className="flex items-center gap-4">

  <div className="text-right">

    <p className="text-sm font-medium">
      Border Officer
    </p>

    <p className="text-xs text-slate-500">
      Checkpoint Alpha
    </p>

  </div>

  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-700">
    <UserRound size={18} />
  </div>

  <button
    onClick={() => {
      localStorage.removeItem("borderguard_authenticated");
      window.location.href = "/login";
    }}
    className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
  >
    Logout
  </button>

</div>

        </header>


        {/* =================================================
            DASHBOARD SECTION
        ================================================= */}

        <section className="p-8">

          {/* TITLE */}

          <div className="mb-8 flex items-center justify-between">

            <div>

              <h3 className="text-2xl font-bold">
                Screening Overview
              </h3>

              <p className="mt-1 text-slate-400">
                Monitor today's border document activity.
              </p>

            </div>


            {/* NEW SCREENING BUTTON */}

            <Link
              to="/screening"
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500"
            >

              <Upload size={18} />

              New Screening

            </Link>

          </div>


          {/* =================================================
              STAT CARDS
          ================================================= */}
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">

            <Stat
              title="Documents Screened"
              value={String(totalScreenings)}
              text="Total documents processed"
              icon={<FileSearch size={20} />}
              type="blue"
            />

            <Stat
              title="Verified"
              value={String(verifiedCount)}
              text="Successfully verified"
              icon={<CheckCircle size={20} />}
              type="green"
            />

            <Stat
              title="Review / Reviewed"
              value={String(reviewCount)}
              text="Review workflow"
              icon={<Clock size={20} />}
              type="yellow"
            />

            <Stat
              title="High Risk"
              value={String(highRiskCount)}
              text="Immediate review"
              icon={<AlertTriangle size={20} />}
              type="red"
            />

          </div>


          {/* =================================================
              RECENT SCREENING
          ================================================= */}

          <div className="mt-8 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

            {/* SECTION HEADER */}

            <div className="flex items-center justify-between border-b border-slate-800 p-6">

              <div>

                <h3 className="font-semibold">
                  Recent Screening Activity
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Latest documents processed by the system
                </p>

              </div>

              <Link
                to="/history"
                className="flex items-center gap-2 text-sm font-medium text-blue-400 hover:text-blue-300"
              >
                View All History
                <Activity size={18} />
              </Link>

            </div>


            {/* TABLE HEADER */}

            <div className="grid grid-cols-5 border-b border-slate-800 px-6 py-3 text-xs uppercase tracking-wider text-slate-500">

              <span>
                ID
              </span>

              <span>
                Applicant
              </span>

              <span>
                Risk
              </span>

              <span>
                Status
              </span>

              <span className="text-right">
                Action
              </span>

            </div>


            {/* ACTIVITY ROWS */}

            <div className="divide-y divide-slate-800">

              {history.length > 0 ? (
                history.slice().reverse().slice(0, 5).map((item: any, index: number) => (
                  <ActivityRow
                    key={index}
                    id={item.id || `#BG-${10232 - index}`}
                    person={
                      item.name ||
                      item.applicant ||
                      "Unknown Applicant"
                    }
                    document={
                      item.documentType ||
                      item.document_type ||
                      "Unknown Document"
                    }
                    risk={`${item.riskScore ?? item.risk_score ?? 0}%`}
                    status={
                      item.status ||
                      (
                        (item.riskScore ?? item.risk_score ?? 0) >= 80
                          ? "HIGH RISK"
                          : (item.riskScore ?? item.risk_score ?? 0) >= 40
                          ? "REVIEW"
                          : "VERIFIED"
                      )
                    }
                  />
                ))
              ) : (
                <div className="px-6 py-8 text-center text-sm text-slate-500">
                  No screening records available.
                </div>
              )}

            </div>

          </div>

                    {/* =================================================
              GATE STATUS
          ================================================= */}

          <div className="mt-8 rounded-xl border border-slate-800 bg-[#080c10]/90 p-6">

            <div className="flex items-center justify-between">

              <div>
                <h3 className="font-semibold text-white">
                  Checkpoint Gate Status
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Current operational status of border checkpoint gates
                </p>
              </div>

              <div className="rounded-lg border border-blue-500/20 bg-blue-500/10 px-3 py-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                  {activeGates}/{totalGates} Active
                </span>
              </div>

            </div>


            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">

              {gates.map((gate) => (

                <div
                  key={gate.id}
                  className="rounded-lg border border-slate-800 bg-[#05080b] p-4"
                >

                  <div className="flex items-center justify-between">

                    <span className="text-xs font-semibold text-slate-300">
                      {gate.gate_code}
                    </span>

                    <span
                      className={`h-2.5 w-2.5 rounded-full ${
                        gate.status === "ACTIVE"
                          ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)]"
                          : "bg-slate-600"
                      }`}
                    />

                  </div>

                  <p
                    className={`mt-3 text-xs font-semibold uppercase tracking-wider ${
                      gate.status === "ACTIVE"
                        ? "text-emerald-400"
                        : "text-slate-500"
                    }`}
                  >
                    {gate.status}
                  </p>

                </div>

              ))}

            </div>

          </div>


          {/* =================================================
              RISK DISTRIBUTION
          ================================================= */}

          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

            <div className="flex items-center justify-between">

              <div>
                <h3 className="font-semibold">
                  Risk Distribution
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Overview of screening risk levels
                </p>
              </div>

              <ShieldCheck
                size={20}
                className="text-blue-400"
              />

            </div>

            <div className="mt-6 space-y-5">

              {/* VERIFIED */}

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <span className="text-sm text-slate-300">
                    Verified
                  </span>

                  <span className="text-sm font-semibold text-emerald-400">
                    {verifiedCount}
                  </span>

                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-800">

                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{
                      width:
                        totalScreenings > 0
                          ? `${(verifiedCount / totalScreenings) * 100}%`
                          : "0%",
                    }}
                  />

                </div>

              </div>


              {/* UNDER REVIEW */}

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <span className="text-sm text-slate-300">
                    Under Review
                  </span>

                  <span className="text-sm font-semibold text-yellow-400">
                    {reviewCount}
                  </span>

                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-800">

                  <div
                    className="h-full rounded-full bg-yellow-500"
                    style={{
                      width:
                        totalScreenings > 0
                          ? `${(reviewCount / totalScreenings) * 100}%`
                          : "0%",
                    }}
                  />

                </div>

              </div>


              {/* HIGH RISK */}

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <span className="text-sm text-slate-300">
                    High Risk
                  </span>

                  <span className="text-sm font-semibold text-red-400">
                    {highRiskCount}
                  </span>

                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-800">

                  <div
                    className="h-full rounded-full bg-red-500"
                    style={{
                      width:
                        totalScreenings > 0
                          ? `${(highRiskCount / totalScreenings) * 100}%`
                          : "0%",
                    }}
                  />

                </div>

              </div>

            </div>

          </div>

          {/* =================================================
    POSTGRESQL SCREENING RECORDS
================================================= */}

<div className="mt-8 overflow-hidden rounded-xl border border-slate-800 bg-[#080c10]/90">

  {/* HEADER */}

  <div className="flex items-center justify-between border-b border-slate-800 p-6">

    <div>
      <h3 className="font-semibold text-white">
        PostgreSQL Screening Records
      </h3>

      <p className="mt-1 text-sm text-slate-400">
        Screening records retrieved from the PostgreSQL database
      </p>
    </div>

    <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2">
      <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
        DATABASE CONNECTED
      </span>
    </div>

  </div>


  {/* TABLE */}

  {history.length > 0 ? (

    <div className="overflow-x-auto">

      <table className="w-full text-left">

        <thead className="border-b border-slate-800 bg-slate-950">

          <tr className="text-xs uppercase tracking-wider text-slate-500">

            <th className="px-6 py-4">
              Screening ID
            </th>

            <th className="px-6 py-4">
              Applicant
            </th>

            <th className="px-6 py-4">
              Document
            </th>

            <th className="px-6 py-4">
              Risk
            </th>

            <th className="px-6 py-4">
              Status
            </th>

            <th className="px-6 py-4">
              Date
            </th>

          </tr>

        </thead>


        <tbody className="divide-y divide-slate-800">

          {history.slice(0, 10).map((item: any, index: number) => (

            <tr
              key={item.id || index}
              className="transition hover:bg-slate-800/40"
            >

              {/* SCREENING ID */}

              <td className="px-6 py-4">

                <span className="font-mono text-xs text-blue-400">
                  {item.id || "N/A"}
                </span>

              </td>


              {/* APPLICANT */}

              <td className="px-6 py-4">

                <span className="text-sm font-medium text-white">
                  {item.name ||
                    item.applicant ||
                    "Unknown Applicant"}
                </span>

              </td>


              {/* DOCUMENT */}

              <td className="px-6 py-4">

                <span className="text-sm text-slate-300">
                  {item.documentType ||
                    item.document_type ||
                    "Unknown"}
                </span>

              </td>


              {/* RISK */}

              <td className="px-6 py-4">

                <span className="font-mono text-sm text-yellow-400">
                  {item.riskScore ??
                    item.risk_score ??
                    0}
                </span>

              </td>


              {/* STATUS */}

              <td className="px-6 py-4">

                <span
                  className={`rounded-md border px-2 py-1 text-xs font-semibold ${
                    item.status === "VERIFIED"
                      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                      : item.status === "HIGH RISK"
                      ? "border-red-500/30 bg-red-500/10 text-red-400"
                      : "border-yellow-500/30 bg-yellow-500/10 text-yellow-400"
                  }`}
                >
                  {item.status || "REVIEW"}
                </span>

              </td>


              {/* DATE */}

              <td className="px-6 py-4">

                <span className="text-xs text-slate-500">
                  {item.date
                    ? new Date(item.date).toLocaleString()
                    : "N/A"}
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  ) : (

    <div className="px-6 py-10 text-center">

      <p className="text-sm text-slate-500">
        No PostgreSQL screening records available.
      </p>

    </div>

  )}

</div>


          {/* =================================================
              SCREENING PERFORMANCE
          ================================================= */}

          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

            <div className="flex items-center justify-between">

              <div>
                <h3 className="font-semibold">
                  Screening Performance
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Current screening statistics
                </p>
              </div>

              <BarChart3
                size={20}
                className="text-blue-400"
              />

            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Total Screenings
                </p>

                <p className="mt-2 text-2xl font-bold text-white">
                  {totalScreenings}
                </p>
                            </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Total Gates
                </p>

                <p className="mt-2 text-2xl font-bold text-blue-400">
                  {totalGates}
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
  <p className="text-xs text-slate-500">
    Active Gates
  </p>

  <p className="mt-2 text-2xl font-bold text-emerald-400">
    {activeGates}
  </p>
</div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Verification Rate
                </p>

                <p className="mt-2 text-2xl font-bold text-emerald-400">
                  {verificationRate}%
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Review Rate
                </p>

                <p className="mt-2 text-2xl font-bold text-yellow-400">
                  {reviewRate}%
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  High Risk Rate
                </p>

                <p className="mt-2 text-2xl font-bold text-red-400">
                  {highRiskRate}%
                </p>
              </div>

            </div>

          </div>

          {/* =================================================
              QUICK ACTIONS
          ================================================= */}

          <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">

            <QuickAction
              icon={<FileSearch size={20} />}
              title="Start Screening"
              description="Upload and analyze a document."
              to="/screening"
            />

            <QuickAction
              icon={<History size={20} />}
              title="View History"
              description="Review previous screenings."
              to="/history"
            />

            <QuickAction
              icon={<BarChart3 size={20} />}
              title="View Analytics"
              description="Monitor security statistics."
              to="/analytics"
            />

          </div>

        </section>

      </main>

    </div>
  );
}


/* =====================================================
   NAVIGATION ITEM
===================================================== */

function NavItem({
  to,
  icon,
  text,
}: {
  to: string;
  icon: ReactNode;
  text: string;
}) {

  const location = useLocation();

  const active =
    location.pathname === to;

  return (
    <Link
      to={to}
      className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm transition ${
        active
          ? "bg-blue-600 text-white"
          : "text-slate-400 hover:bg-slate-800 hover:text-white"
      }`}
    >

      {icon}

      <span>
        {text}
      </span>

    </Link>
  );
}


/* =====================================================
   STAT CARD
===================================================== */

function Stat({
  title,
  value,
  text,
  icon,
  type,
}: {
  title: string;
  value: string;
  text: string;
  icon: ReactNode;
  type: "blue" | "green" | "yellow" | "red";
}) {

  const iconStyles = {
    blue: "bg-blue-500/10 text-blue-400",
    green: "bg-emerald-500/10 text-emerald-400",
    yellow: "bg-yellow-500/10 text-yellow-400",
    red: "bg-red-500/10 text-red-400",
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700">

      <div className="flex items-center justify-between">

        <p className="text-sm text-slate-400">
          {title}
        </p>

        <div
          className={`rounded-lg p-2 ${iconStyles[type]}`}
        >
          {icon}
        </div>

      </div>


      <p className="mt-4 text-3xl font-bold">
        {value}
      </p>


      <p className="mt-1 text-xs text-slate-500">
        {text}
      </p>

    </div>
  );
}


/* =====================================================
   ACTIVITY ROW
===================================================== */

function ActivityRow({
  id,
  person,
  document,
  risk,
  status,
}: {
  id: string;
  person: string;
  document: string;
  risk: string;
  status: string;
}) {

  const statusStyle =
    status === "VERIFIED"
      ? "bg-emerald-500/10 text-emerald-400"
      : status === "REVIEW"
      ? "bg-yellow-500/10 text-yellow-400"
      : "bg-red-500/10 text-red-400";


  const riskNumber =
    parseInt(risk.replace("%", ""), 10);


  const riskStyle =
    riskNumber >= 80
      ? "text-red-400"
      : riskNumber >= 40
      ? "text-yellow-400"
      : "text-emerald-400";


  return (
    <div className="grid grid-cols-5 items-center px-6 py-5 transition hover:bg-slate-800/40">

      {/* ID */}

      <span className="text-sm text-slate-500">
        {id}
      </span>


      {/* PERSON */}

      <div>

        <p className="text-sm font-medium">
          {person}
        </p>

        <p className="text-xs text-slate-500">
          {document}
        </p>

      </div>


      {/* RISK */}

      <span className={`text-sm font-semibold ${riskStyle}`}>
        {risk}
      </span>


      {/* STATUS */}

      <span
        className={`w-fit rounded-full px-3 py-1 text-xs font-medium ${statusStyle}`}
      >
        {status}
      </span>


      {/* VIEW */}

      <Link
        to="/screening"
        className="ml-auto flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300"
      >

        View

        <ChevronRight size={16} />

      </Link>

    </div>
  );
}


/* =====================================================
   QUICK ACTION
===================================================== */

function QuickAction({
  icon,
  title,
  description,
  to,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  to: string;
}) {

  return (
    <Link
      to={to}
      className="group rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-blue-500/40 hover:bg-slate-900/80"
    >

      <div className="mb-4 flex items-center justify-between">

        <div className="rounded-lg bg-blue-500/10 p-2 text-blue-400">
          {icon}
        </div>

        <ChevronRight
          size={18}
          className="text-slate-600 transition group-hover:text-blue-400"
        />

      </div>


      <h4 className="font-semibold">
        {title}
      </h4>


      <p className="mt-1 text-sm text-slate-500">
        {description}
      </p>

    </Link>
  );
}


/* =====================================================
   EXPORT
===================================================== */

export default App;