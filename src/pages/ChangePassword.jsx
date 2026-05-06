import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";
import { apiService } from "../services/api.js";

export default function ChangePassword() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const user = userStore.getCurrentUser();
  const isResetFlow = params.get("reset") === "true";
  const resetEmail = params.get("email") || "";
  const resetCode = params.get("code") || "";

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    if (newPwd !== confirmPwd) {
      setError("Les mots de passe ne correspondent pas");
      setLoading(false);
      return;
    }

    if (newPwd.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères");
      setLoading(false);
      return;
    }

    // Password strength validation (same as backend)
    const strongPassword = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$/;
    if (!strongPassword.test(newPwd)) {
      setError("Le mot de passe doit contenir: majuscule, minuscule, chiffre, et caractère spécial");
      setLoading(false);
      return;
    }

    try {
      if (isResetFlow) {
        // Password reset flow - use localStorage userStore for now
        const result = userStore.resetPassword(resetEmail, resetCode, newPwd);
        if (!result.success) {
          throw new Error(result.error);
        }
        setSuccess("Mot de passe réinitialisé avec succès");
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          navigate("/se-connecter", { replace: true });
        }, 2000);
      } else {
        // Regular password change flow - requires OTP
        if (!showOtpInput) {
          // First step: check authentication and send OTP
          if (!apiService.isAuthenticated()) {
            throw new Error("Vous devez être connecté pour changer votre mot de passe");
          }
          
          await apiService.sendPasswordOtp();
          setShowOtpInput(true);
          setSuccess("Code de vérification envoyé à votre email");
          setLoading(false);
          return;
        }
        
        // Second step: change password with OTP
        if (!otpCode || otpCode.trim() === '') {
          setError("Le code de vérification est requis");
          setLoading(false);
          return;
        }
        
        await apiService.changePassword(currentPwd, newPwd, otpCode);
        setSuccess("Mot de passe changé avec succès");
        
        // Redirect after 2 seconds
        setTimeout(() => {
          navigate("/bienvenue", { replace: true });
        }, 2000);
      }
      
      // Clear form after success
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");
      setOtpCode("");
      setShowOtpInput(false);
    } catch (error) {
      console.error('Change password error:', error);
      let errorMessage = "Erreur lors du changement de mot de passe";
      
      if (error.message) {
        if (error.message.includes('current password')) {
          errorMessage = "Mot de passe actuel incorrect";
        } else if (error.message.includes('validation')) {
          errorMessage = "Vérifiez les informations saisies";
        } else if (error.message.length < 100) {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if ((!user || !apiService.isAuthenticated()) && !isResetFlow) {
    return (
      <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
        <div className="text-center">
          <p className="mb-4 text-gray-300">Vous devez être connecté pour accéder à cette page</p>
          <button 
            onClick={() => navigate("/se-connecter")}
            className="rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition"
          >
            Se connecter
          </button>
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
              <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" strokeWidth="2" />
              <path d="M8 11V7a4 4 0 018 0v4" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
          <h1 className="font-serif text-2xl">
            {isResetFlow ? "Réinitialiser le mot de passe" : "Changer le mot de passe"}
          </h1>
          <p className="mt-1 text-sm text-gray-300">
            {isResetFlow 
              ? `Définissez un nouveau mot de passe pour ${resetEmail}`
              : "Modifiez votre mot de passe de connexion"
            }
          </p>
        </div>

        <form onSubmit={submit} className="mt-8 space-y-4">
          {!isResetFlow && (
            <div>
              <label className="block text-xs text-gray-300 mb-1">
                Mot de passe actuel
              </label>
              <input
                type="password"
                required
                value={currentPwd}
                onChange={(e) => setCurrentPwd(e.target.value)}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              Nouveau mot de passe
            </label>
            <input
              type="password"
              required
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
            <p className="text-xs text-gray-400 mt-1">8+ chars, majuscule, minuscule, chiffre, caractère spécial</p>
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              Confirmer le nouveau mot de passe
            </label>
            <input
              type="password"
              required
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>

          {showOtpInput && !isResetFlow && (
            <div>
              <label className="block text-xs text-gray-300 mb-1">
                Code de vérification
              </label>
              <input
                type="text"
                required
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
              />
              <p className="text-xs text-gray-400 mt-1">Code à 6 chiffres reçu par email</p>
            </div>
          )}

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
            {loading ? "Chargement..." : (isResetFlow ? "Réinitialiser le mot de passe" : (showOtpInput ? "Confirmer le changement" : "Envoyer le code de vérification"))}
          </button>

          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => navigate("/bienvenue")}
              className="text-sm text-gray-300 hover:text-white transition"
            >
              Retour au tableau de bord
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
