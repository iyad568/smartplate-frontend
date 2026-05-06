import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { apiService } from "../services/api.js";

export default function SendOtpPassword() {
  const { t } = useLang();
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1 = send OTP, 2 = verify OTP
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const requestCode = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await apiService.resendOtp(email, "RESET");
      setSuccess("Code de réinitialisation envoyé à votre adresse email");
      setStep(2);
    } catch (error) {
      console.error('Send OTP error:', error);
      let errorMessage = "Erreur lors de l'envoi du code";
      
      if (error.message) {
        if (error.message.includes('not found') || error.message.includes('exists')) {
          errorMessage = "Aucun compte trouvé avec cet email";
        } else if (error.message.includes('rate limit')) {
          errorMessage = "Veuillez attendre avant de demander un nouveau code";
        } else if (error.message.length < 100) {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      // For now, use the existing userStore OTP verification
      // Backend integration will be added later
      const result = userStore.verifyCode(email, code);
      if (!result.success) {
        throw new Error(result.error);
      }
      
      // Navigate to change password page with email and code context
      navigate(`/dashboard/change-password?email=${encodeURIComponent(email)}&code=${code}&reset=true`, { replace: true });
    } catch (error) {
      console.error('OTP verification error:', error);
      let errorMessage = "Erreur lors de la vérification du code";
      
      if (error.message) {
        if (error.message.includes('invalid') || error.message.includes('incorrect')) {
          errorMessage = "Code de réinitialisation invalide";
        } else if (error.message.includes('expired')) {
          errorMessage = "Code expiré. Veuillez demander un nouveau code";
        } else if (error.message.length < 100) {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
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
          <h1 className="font-serif text-2xl">
            {step === 1 ? "Réinitialiser le mot de passe" : "Vérifier le code"}
          </h1>
          <p className="mt-1 text-sm text-gray-300">
            {step === 1 
              ? "Entrez votre email pour recevoir un code de réinitialisation" 
              : "Entrez le code reçu pour continuer"
            }
          </p>
        </div>

        {step === 1 ? (
          <form onSubmit={requestCode} className="mt-8 space-y-4">
            <div>
              <label className="block text-xs text-gray-300 mb-1">
                Adresse email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="votre@gmail.com"
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
              <p className="text-xs text-gray-400 mt-1">Doit être une adresse Gmail (@gmail.com)</p>
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
              disabled={loading}
              className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Envoi en cours..." : "Envoyer le code"}
            </button>

            <div className="text-center mt-4">
              <Link
                to="/se-connecter"
                className="text-sm text-gray-300 hover:text-white transition"
              >
                Retour à la connexion
              </Link>
            </div>
          </form>
        ) : (
          <form onSubmit={verifyOtp} className="mt-8 space-y-4">
            <div>
              <label className="block text-xs text-gray-300 mb-1">
                Code de réinitialisation
              </label>
              <input
                type="text"
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
              <p className="text-xs text-gray-400 mt-1">Code à 6 chiffres reçu par email</p>
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
              disabled={loading}
              className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Vérification en cours..." : "Vérifier le code"}
            </button>

            <div className="text-center mt-4 space-y-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-sm text-gray-300 hover:text-white transition block"
              >
                Demander un nouveau code
              </button>
              <Link
                to="/se-connecter"
                className="text-sm text-gray-300 hover:text-white transition block"
              >
                Retour à la connexion
              </Link>
            </div>
          </form>
        )}
      </div>
    </section>
  );
}
