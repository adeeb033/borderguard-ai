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
} from "react-router-dom";

import type { ReactNode } from "react";

import NewScreening from "./pages/NewScreening";
import ScreeningHistory from "./pages/ScreeningHistory";
import SecurityAlerts from "./pages/SecurityAlerts";
import Analytics from "./pages/Analytics";

/* =====================================================
   MAIN APP
===================================================== */

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Dashboard */}
        <Route path="/" element={<Dashboard />} />

        {/* New Screening */}
        <Route
          path="/screening"
          element={<NewScreening />}
        />

        {/* Screening History */}
        <Route
  path="/history"
  element={<ScreeningHistory />}
/>

        {/* Security Alerts */}
        <Route
  path="/alerts"
  element={<SecurityAlerts />}
/>

        {/* Analytics */}
        <Route
  path="/analytics"
  element={<Analytics />}
/>

      </Routes>
    </BrowserRouter>
  );
}


/* =====================================================
   DASHBOARD
===================================================== */

function Dashboard() {

  const history = JSON.parse(
    localStorage.getItem("borderguard_history") || "[]"
  );

  const totalScreenings = history.length;

  const verifiedCount = history.filter(
    (item: any) => item.status === "VERIFIED"
  ).length;

  const reviewCount = history.filter(
    (item: any) => item.status === "REVIEW"
  ).length;

  const highRiskCount = history.filter(
    (item: any) =>
      item.riskLevel === "HIGH" ||
      item.status === "HIGH RISK"
  ).length;

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-slate-800 bg-slate-900">

        {/* LOGO */}

        <div className="flex items-center gap-3 border-b border-slate-800 p-6">

          <div className="rounded-xl bg-blue-600 p-3">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h1 className="font-bold">
              BorderGuard
            </h1>

            <p className="text-xs text-slate-400">
              AI Screening System
            </p>
          </div>

        </div>


        {/* NAVIGATION */}

        <nav className="space-y-2 p-4">

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


        {/* SYSTEM STATUS */}

        <div className="absolute bottom-0 w-full border-t border-slate-800 p-5">

          <p className="text-xs text-slate-500">
            SYSTEM STATUS
          </p>

          <div className="mt-2 flex items-center gap-2">

            <span className="h-2 w-2 rounded-full bg-green-500" />

            <span className="text-sm text-green-400">
              Operational
            </span>

          </div>

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

          <div className="flex items-center gap-3">

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
    title="Under Review"
    value={String(reviewCount)}
    text="Requires attention"
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

              <Activity
                size={20}
                className="text-blue-400"
              />

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
  history.slice().reverse().map((item: any, index: number) => (
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
   PLACEHOLDER PAGE
===================================================== */

function Placeholder({
  title,
}: {
  title: string;
}) {

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Simple top bar */}

      <header className="border-b border-slate-800 bg-slate-900 px-8 py-5">

        <div className="flex items-center gap-3">

          <div className="rounded-lg bg-blue-600 p-2">

            <ShieldCheck size={20} />

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

      </header>


      {/* Content */}

      <main className="flex min-h-[calc(100vh-85px)] items-center justify-center p-8">

        <div className="max-w-md text-center">

          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">

            <ShieldCheck size={32} />

          </div>


          <h1 className="text-2xl font-bold">
            {title}
          </h1>


          <p className="mt-3 text-slate-400">
            This module is ready for the next development stage.
          </p>


          <Link
            to="/"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500"
          >

            <LayoutDashboard size={18} />

            Back to Dashboard

          </Link>

        </div>

      </main>

    </div>
  );
}


/* =====================================================
   EXPORT
===================================================== */

export default App;