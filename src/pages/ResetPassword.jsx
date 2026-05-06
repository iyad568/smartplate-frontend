import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";

export default function ResetPassword() {
  const { t } = useLang();
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1 = ask email, 2 = code + new pwd
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [demoCode, setDemoCode] = useState("");

  const requestCode = (e) => {
    e.preventDefault();
    setError("");
    if (!userStore.emailExists(email)) {
      setError(t("reset_email_not_found"));
      return;
    }
    const c = userStore.issueCode(email, "reset");
    setDemoCode(c);
    setStep(2);
  };

  const submit = (e) => {
    e.preventDefault();
    setError("");
    if (newPwd !== confirmPwd) {
      setError(t("reset_password_mismatch"));
      return;
    }
    if (newPwd.length < 4) {
      setError(t("reset_password_too_short"));
      return;
    }
    const r = userStore.resetPassword(email, code, newPwd);
    if (!r.success) {
      setError(r.error);
      return;
    }
    setSuccess(t("reset_success"));
    setTimeout(() => navigate("/se-connecter", { replace: true }), 1500);
  };

  return (
    <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/10 mb-3">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
              <path d="M8 11V7a4 4 0 018 0v4" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
          <h1 className="font-serif text-2xl">{t("reset_title")}</h1>
          <p className="mt-1 text-sm text-gray-300">
            {step === 1 ? t("reset_step1_sub") : t("reset_step2_sub")}
          </p>
        </div>

        {step === 1 ? (
          <form onSubmit={requestCode} className="mt-8 space-y-4">
            <div>
              <label className="block text-xs text-gray-300 mb-1">
                {t("login_email")}
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
            </div>

            {error && (
              <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/30 rounded-md p-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition"
            >
              {t("reset_send_code")}
            </button>
          </form>
        ) : (
          <form onSubmit={submit} className="mt-8 space-y-4">
            {demoCode && (
              <div className="rounded-md border border-yellow-500/30 bg-yellow-500/10 p-3 text-center">
                <p className="text-xs text-yellow-200 mb-1">
                  {t("verify_demo_label")}
                </p>
                <p className="font-mono text-2xl tracking-widest text-yellow-100">
                  {demoCode}
                </p>
              </div>
            )}

            <div>
              <label className="block text-xs text-gray-300 mb-1">
                {t("verify_code_label")}
              </label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                required
                value={code}
                onChange={(e) =>
                  setCode(e.target.value.replace(/\D/g, "").slice(0, 6))
                }
                placeholder="123456"
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 text-center text-xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-white/60"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-300 mb-1">
                {t("reset_new_password")}
              </label>
              <input
                type="password"
                required
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-300 mb-1">
                {t("reset_confirm_password")}
              </label>
              <input
                type="password"
                required
                value={confirmPwd}
                onChange={(e) => setConfirmPwd(e.target.value)}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
            </div>

            {error && (
              <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/30 rounded-md p-2">
                {error}
              </p>
            )}
            {success && (
              <p className="text-sm text-green-300 bg-green-500/10 border border-green-500/30 rounded-md p-2">
                {success}
              </p>
            )}

            <button
              type="submit"
              className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition"
            >
              {t("reset_submit")}
            </button>

            <button
              type="button"
              onClick={() => setStep(1)}
              className="w-full rounded-md border border-white/20 text-gray-200 px-4 py-2 text-sm hover:bg-white/5 transition"
            >
              ← {t("reset_change_email")}
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-sm">
          <Link
            to="/se-connecter"
            className="text-gray-300 hover:text-white"
          >
            ← {t("login_submit")}
          </Link>
        </div>
      </div>
    </section>
  );
}
