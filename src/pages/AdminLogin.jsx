import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { adminAuth } from "../admin/store.js";

export default function AdminLogin() {
  const { t } = useLang();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || "/admin/sos";

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = (e) => {
    e.preventDefault();
    if (adminAuth.login(form.email, form.password)) {
      navigate(redirectTo, { replace: true });
    } else {
      setError(t("admin_login_error"));
    }
  };

  return (
    <section className="bg-[#0b1d3a] min-h-[80vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/10 mb-3">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2l8 4v6c0 5-4 8-8 10-4-2-8-5-8-10V6l8-4z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h1 className="font-serif text-2xl">{t("admin_title")}</h1>
          <p className="mt-1 text-sm text-gray-300">{t("admin_subtitle")}</p>
        </div>

        <form onSubmit={onSubmit} className="mt-8 space-y-4">
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("login_email")}
            </label>
            <input
              type="email"
              name="email"
              required
              value={form.email}
              onChange={onChange}
              className="w-full rounded-md bg-white/95 text-gray-900 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-white/60"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-300 mb-1">
              {t("login_password")}
            </label>
            <input
              type="password"
              name="password"
              required
              value={form.password}
              onChange={onChange}
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
            {t("admin_login_btn")}
          </button>
        </form>

        <p className="mt-6 text-xs text-gray-400 text-center">
          {t("admin_demo_hint")}
        </p>

        <div className="mt-3 text-center">
          <Link
            to="/"
            className="text-xs text-gray-300 hover:text-white underline"
          >
            ← {t("nav_home")}
          </Link>
        </div>
      </div>
    </section>
  );
}
