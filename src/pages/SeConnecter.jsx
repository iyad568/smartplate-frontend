import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { userStore } from "../admin/store.js";

export default function SeConnecter() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  return (
    <section className="bg-[#0b1d3a] min-h-[70vh] grid place-items-center text-white py-16">
      <div className="w-full max-w-md mx-auto bg-[#0e2249] border border-white/10 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <h1 className="font-serif text-3xl">{t("login_title")}</h1>
          <p className="mt-1 text-sm text-gray-300">{t("login_sub")}</p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            const result = userStore.authenticate(form.email, form.password);
            if (result.success) {
              setError("");
              // Redirect based on role
              if (result.user.role === "user") {
                navigate("/dashboard");
              } else if (result.user.role === "sos") {
                navigate("/operator/sos");
              } else if (result.user.role === "depannage") {
                navigate("/operator/depannage");
              }
            } else {
              setError(result.error);
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

          <button
            type="submit"
            className="w-full rounded-md bg-white text-navy-900 font-semibold px-4 py-2.5 hover:bg-gray-100 transition"
          >
            {t("login_submit")}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-between text-sm">
          <a href="#" className="text-gray-300 hover:text-white">
            {t("login_forgot")}
          </a>
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
