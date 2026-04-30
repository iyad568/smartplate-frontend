import { useState } from "react";
import { useLang } from "../i18n.jsx";
import { sosStore } from "../admin/store.js";

export default function Sos() {
  const { t } = useLang();
  const [form, setForm] = useState({
    name: "",
    plate: "",
    email: "",
    desc: "",
    location: "",
  });
  const [sent, setSent] = useState(false);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = (e) => {
    e.preventDefault();
    sosStore.add(form);
    setSent(true);
    setForm({ name: "", plate: "", email: "", desc: "", location: "" });
  };

  const useGps = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setForm((f) => ({
          ...f,
          location: `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`,
        }));
      },
      () => {
        // ignore — user can type manually
      }
    );
  };

  const inputClass =
    "w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500/40 bg-white";

  return (
    <section className="bg-gradient-to-br from-red-50 via-white to-red-100 min-h-[80vh]">
      <div className="container-x py-16 grid lg:grid-cols-5 gap-10 items-start">
        {/* Form on the left */}
        <form
          onSubmit={onSubmit}
          className="lg:col-span-3 bg-white rounded-2xl border border-red-100 shadow-md p-6 md:p-8 space-y-5"
        >
          <h1 className="font-serif text-3xl md:text-4xl text-red-600 flex items-center gap-3">
            <span className="inline-flex items-center justify-center bg-red-600 text-white rounded-md w-12 h-12 font-bold">
              SOS
            </span>
            <span>{t("sos_title")}</span>
          </h1>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("sos_full_name")}
              </label>
              <input
                name="name"
                required
                value={form.name}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("sos_plate")}
              </label>
              <input
                name="plate"
                required
                value={form.plate}
                onChange={onChange}
                className={inputClass}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {t("sos_email")}
            </label>
            <input
              type="email"
              name="email"
              required
              value={form.email}
              onChange={onChange}
              className={inputClass}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {t("sos_desc")}
            </label>
            <textarea
              name="desc"
              required
              rows={4}
              value={form.desc}
              onChange={onChange}
              className={inputClass}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {t("sos_location")}
            </label>
            <div className="flex gap-2">
              <input
                name="location"
                value={form.location}
                onChange={onChange}
                placeholder="Lat, Lng"
                className={inputClass}
              />
              <button
                type="button"
                onClick={useGps}
                className="rounded-md bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 text-sm font-medium border border-gray-200 whitespace-nowrap"
              >
                {t("sos_use_gps")}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full rounded-md bg-red-600 text-white font-semibold py-3 hover:bg-red-700 transition flex items-center justify-center gap-2"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
            </svg>
            {t("sos_submit")}
          </button>

          {sent && (
            <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-md p-3">
              ✓ {t("sos_submit")} — OK
            </p>
          )}
        </form>

        {/* SOS visual on the right */}
        <aside className="lg:col-span-2 lg:sticky lg:top-24 space-y-4">
          <div className="rounded-2xl bg-white border border-red-100 shadow-md overflow-hidden">
            <div className="aspect-square bg-gradient-to-br from-red-500 to-red-700 grid place-items-center p-8">
              <img
                src="/sos.jpg"
                alt="SOS"
                className="w-full h-full object-contain drop-shadow-2xl"
                loading="lazy"
              />
            </div>
            <div className="p-5 text-center">
              <h3 className="font-serif text-xl text-navy-900">
                {t("about_assistance")}
              </h3>
              <p className="mt-1 text-sm text-gray-600">{t("about_phone")}</p>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
