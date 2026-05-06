import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";
import { apiService } from "../services/api.js";

export default function NouveauContact() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullname: "",
    email: "",
    phone: "+213",
    password: "",
    confirm: "",
    role: "user",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    
    setLoading(true);
    setError("");

    try {
      // Call backend API to signup
      await apiService.signup({
        fullname: form.fullname,
        email: form.email,
        phone: form.phone,
        password: form.password,
        confirm: form.confirm,
        role: form.role,
      });

      // Success - navigate to OTP verification page
      navigate(
        `/verify-email?email=${encodeURIComponent(form.email)}&reason=signup`
      );
    } catch (error) {
      console.error('Registration error:', error);
      let errorMessage = "Erreur lors de l'inscription";
      
      if (error.message) {
        // Try to extract meaningful error message
        if (error.message.includes('already registered')) {
          errorMessage = "Cet email est déjà enregistré";
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

  return (
    <section className="bg-[#0b1d3a] min-h-[80vh] py-16 text-white">
      <div className="container-x">
        <h1 className="font-serif text-3xl md:text-5xl text-center text-gray-200/40 mb-10">
          {t("reg_title")}
        </h1>

        <form
          onSubmit={onSubmit}
          className="w-full max-w-xl mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8 space-y-5"
        >
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("reg_fullname")}
            </label>
            <input
              name="fullname"
              required
              value={form.fullname}
              onChange={onChange}
              placeholder="Your name"
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("reg_email")}
            </label>
            <input
              name="email"
              type="email"
              required
              value={form.email}
              onChange={onChange}
              placeholder="exemple@gmail.com"
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
            <p className="text-xs text-gray-400 mt-1">Doit être une adresse Gmail (@gmail.com)</p>
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("reg_phone")}
            </label>
            <input
              name="phone"
              type="tel"
              required
              value={form.phone}
              onChange={onChange}
              placeholder="+213555123456"
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
            <p className="text-xs text-gray-400 mt-1">Format international: +213555123456</p>
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              Type de compte
            </label>
            <select
              name="role"
              required
              value={form.role}
              onChange={onChange}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            >
              <option value="user">Utilisateur standard</option>
              <option value="sos">Opérateur SOS</option>
              <option value="depannage">Opérateur Dépannage</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("reg_password")}
            </label>
            <input
              name="password"
              type="password"
              required
              value={form.password}
              onChange={onChange}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
            <p className="text-xs text-gray-400 mt-1">8+ chars, majuscule, minuscule, chiffre, caractère spécial</p>
          </div>

          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("reg_password_confirm")}
            </label>
            <input
              name="confirm"
              type="password"
              required
              value={form.confirm}
              onChange={onChange}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>

          {error && (
            <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-md p-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "Inscription..." : t("reg_submit")}
          </button>

          <div className="pt-3 text-center text-sm text-gray-300 border-t border-white/10">
            <span>{t("reg_have_account")} </span>
            <Link
              to="/se-connecter"
              className="text-white font-medium hover:underline"
            >
              {t("reg_login_link")}
            </Link>
          </div>
        </form>
      </div>
    </section>
  );
}
