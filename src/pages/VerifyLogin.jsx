import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { apiService } from "../services/api.js";
import { userStore } from "../admin/store.js";

export default function VerifyLogin() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const preAuthToken = params.get("preAuthToken") || "";

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resentAt, setResentAt] = useState(null);

  useEffect(() => {
    // Check if we have the required parameters
    if (!email || !preAuthToken) {
      navigate("/se-connecter");
    }
  }, [email, preAuthToken, navigate]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!code) {
      setError("Veuillez entrer le code de vérification");
      return;
    }
    
    setLoading(true);
    setError("");

    try {
      // Verify login OTP
      const result = await apiService.verifyLoginOtp(email, code, preAuthToken);

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
      console.error('Login OTP verification error:', error);
      let errorMessage = "Code de vérification invalide";
      
      if (error.message) {
        if (error.message.includes('No active code') || error.message.includes('expired')) {
          errorMessage = "Code expiré. Veuillez demander un nouveau code.";
        } else if (error.message.includes('invalid') || error.message.includes('incorrect')) {
          errorMessage = "Code incorrect. Veuillez réessayer.";
        } else if (error.message.length < 100) {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const resend = async () => {
    if (!email) return;
    
    setLoading(true);
    setError("");

    try {
      await apiService.resendOtp(email, "LOGIN");
      setResentAt(new Date().toLocaleTimeString());
      setError("Code de connexion renvoyé avec succès");
    } catch (error) {
      setError(error.message || "Erreur lors du renvoi du code");
    } finally {
      setLoading(false);
    }
  };

  if (!email || !preAuthToken) {
    return (
      <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
        <div className="text-center">
          <p className="mb-4 text-gray-300">Paramètres de connexion manquants</p>
          <Link
            to="/se-connecter"
            className="text-white underline hover:no-underline"
          >
            Retour à la connexion
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <h1 className="font-serif text-2xl">
            {t("verify_title")}
          </h1>
          <p className="mt-1 text-sm text-gray-300">
            Code de vérification envoyé à{" "}
            <span className="text-white font-medium">{email}</span>
          </p>
        </div>

        <div className="mt-6 rounded-md border border-yellow-500/30 bg-yellow-500/10 p-3 text-center">
          <p className="text-xs text-yellow-200">
            Vérifiez votre email pour le code de connexion
          </p>
        </div>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              Code de vérification
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
            {loading ? "Vérification..." : "Se connecter"}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-between text-sm">
          <button
            type="button"
            onClick={resend}
            disabled={loading}
            className="text-gray-300 hover:text-white disabled:cursor-not-allowed"
          >
            Renvoyer le code
          </button>
          <Link
            to="/se-connecter"
            className="text-gray-300 hover:text-white"
          >
            Retour
          </Link>
        </div>
      </div>
    </section>
  );
}
