import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";
import { apiService } from "../services/api.js";

export default function SeConnecter() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isUnverified, setIsUnverified] = useState(false);
  const [resending, setResending] = useState(false);

  const handleResendAndVerify = async () => {
    setResending(true);
    setError("");
    try {
      await apiService.resendOtp(form.email, "signup");
      navigate(`/verify-email?email=${encodeURIComponent(form.email)}&reason=signup`);
    } catch (err) {
      setError(err.message || "Erreur lors du renvoi du code");
    } finally {
      setResending(false);
    }
  };

  return (
    <section className="bg-[#0b1d3a] min-h-[70vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <h1 className="font-serif text-3xl">{t("login_title")}</h1>
          <p className="mt-1 text-sm text-gray-300">{t("login_sub")}</p>
        </div>

        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setLoading(true);
            setError("");

            try {
              // Step 1: Login with password
              const loginResult = await apiService.login(form.email, form.password);

              // Step 2: Navigate to OTP verification page
              navigate(
                `/verify-login?email=${encodeURIComponent(form.email)}&preAuthToken=${loginResult.pre_auth_token}`
              );
            } catch (err) {
              const msg = err.message || "Identifiants invalides";
              // 403 = email not verified → offer resend shortcut
              if (msg.toLowerCase().includes("verify your email") || msg.includes("403")) {
                setIsUnverified(true);
              }
              setError(msg);
            } finally {
              setLoading(false);
            }
          }}
          className="mt-8 space-y-4"
        >
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("login_email")}
            </label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("login_password")}
            </label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>

          {error && (
            <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-md p-2">
              {error}
            </p>
          )}

          {isUnverified && (
            <div className="rounded-md border border-yellow-500/40 bg-yellow-500/10 p-3 text-sm text-yellow-200 space-y-2">
              <p className="font-medium">📧 Votre email n'est pas encore vérifié.</p>
              <p className="text-xs text-yellow-300">
                Cliquez ci-dessous pour recevoir un nouveau code de vérification, puis entrez-le sur la page suivante.
              </p>
              <button
                type="button"
                disabled={resending}
                onClick={handleResendAndVerify}
                className="w-full rounded-md bg-yellow-400 text-gray-900 font-semibold px-4 py-2 hover:bg-yellow-300 transition disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {resending ? "Envoi en cours..." : "Renvoyer le code & vérifier →"}
              </button>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "Connexion..." : t("login_submit")}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-between text-sm">
          <Link
            to="/dashboard/send-otp-password"
            className="text-gray-300 hover:text-white"
          >
            {t("login_forgot")}
          </Link>
          <Link
            to="/nouveau-contact"
            className="text-gray-300 hover:text-white"
          >
            {t("login_create")}
          </Link>
        </div>
        <p className="mt-3 text-center text-xs text-gray-400">
          {t("login_no_account")}
        </p>
      </div>
    </section>
  );
}
