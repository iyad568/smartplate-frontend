import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";
import { apiService } from "../services/api.js";

export default function VerifyEmail() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const reason = params.get("reason") || "login";

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resentAt, setResentAt] = useState(null);

  useEffect(() => {
    // For demo purposes, show a hint about the OTP
    // In production, user would receive OTP via email
  }, [email, reason]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!code) {
      setError("Veuillez entrer le code de vérification");
      return;
    }
    
    setLoading(true);
    setError("");

    try {
      let result;
      if (reason === "signup") {
        // Verify email for signup
        result = await apiService.verifyEmail(email, code);
      } else {
        // This would be for login OTP verification (not implemented yet)
        throw new Error("Login OTP verification not implemented");
      }

      // Store tokens and user data
      apiService.setTokens(result.access_token, result.refresh_token);
      
      // Get current user info
      const currentUser = await apiService.getCurrentUser();
      
      // Store in local store with actual user data
      userStore.setCurrentUser(currentUser);
      
      // Route based on the verified user's role
      if (currentUser.role === "sos") navigate("/operator/sos", { replace: true });
      else if (currentUser.role === "depannage")
        navigate("/operator/depannage", { replace: true });
      else navigate("/bienvenue", { replace: true });
    } catch (error) {
      setError(error.message || "Code de vérification invalide");
    } finally {
      setLoading(false);
    }
  };

  const resend = async () => {
    if (!email) return;
    
    setLoading(true);
    setError("");

    try {
      await apiService.resendOtp(email, reason === "signup" ? "signup" : "login");
      setResentAt(new Date().toLocaleTimeString());
      setError("Code renvoyé avec succès");
    } catch (error) {
      setError(error.message || "Erreur lors du renvoi du code");
    } finally {
      setLoading(false);
    }
  };

  if (!email) {
    return (
      <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
        <div className="text-center">
          <p className="mb-4 text-gray-300">{t("verify_no_email")}</p>
          <Link
            to="/se-connecter"
            className="text-white underline hover:no-underline"
          >
            {t("login_submit")}
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/10 mb-3">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 8l9 6 9-6M3 8v10a2 2 0 002 2h14a2 2 0 002-2V8M3 8l9-5 9 5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h1 className="font-serif text-2xl">
            {reason === "reset" ? t("verify_reset_title") : t("verify_title")}
          </h1>
          <p className="mt-1 text-sm text-gray-300">
            {t("verify_sent_to")}{" "}
            <span className="text-white font-medium">{email}</span>
          </p>
        </div>

        {/* Demo code notice — for development only */}
        <div className="mt-6 rounded-md border border-yellow-500/30 bg-yellow-500/10 p-3 text-center">
          <p className="text-xs text-yellow-200 mb-1">
            Pour le développement: vérifiez votre email ou utilisez le code de démonstration
          </p>
          <p className="font-mono text-sm text-yellow-100">
            Le code est envoyé à: {email}
          </p>
        </div>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
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
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-3 text-center text-2xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>

          {error && (
            <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/30 rounded-md p-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "Vérification..." : t("verify_submit")}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-between text-sm">
          <button
            type="button"
            onClick={resend}
            className="text-gray-300 hover:text-white"
          >
            {t("verify_resend")}
          </button>
          <Link
            to="/se-connecter"
            className="text-gray-300 hover:text-white"
          >
            ← {t("login_submit")}
          </Link>
        </div>

        {resentAt && (
          <p className="mt-3 text-xs text-green-300 text-center">
            ✓ {t("verify_resent")} ({resentAt})
          </p>
        )}
      </div>
    </section>
  );
}
