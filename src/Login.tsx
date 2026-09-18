import { useState } from "react";

type LoginProps = {
  onLogin: () => void;
};

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    setError("");

    // Demo officer credentials
    if (username === "officer" && password === "border123") {
      onLogin();
    } else {
      setError("Invalid username or password.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-8 shadow-2xl">
          
          {/* Logo / Title */}
          <div className="text-center mb-8">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600/20">
              <span className="text-3xl">🛡️</span>
            </div>

            <h1 className="text-3xl font-bold text-white">
              BorderGuard AI
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Border Document Screening Platform
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-5">
            
            {/* Username */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Officer Username
              </label>

              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Password */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
                <p className="text-sm text-red-400">
                  {error}
                </p>
              </div>
            )}

            {/* Login Button */}
            <button
              type="submit"
              className="w-full rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-500"
            >
              Login
            </button>
          </form>

          {/* Demo information */}
          <div className="mt-6 rounded-lg border border-slate-700 bg-slate-950 p-4">
            <p className="text-xs text-slate-500">
              Demo Officer Account
            </p>

            <p className="mt-2 text-sm text-slate-300">
              Username: <span className="font-semibold">officer</span>
            </p>

            <p className="mt-1 text-sm text-slate-300">
              Password: <span className="font-semibold">border123</span>
            </p>
          </div>

          <p className="mt-6 text-center text-xs text-slate-500">
            AI assists. Officer decides.
          </p>
        </div>
      </div>
    </div>
  );
}