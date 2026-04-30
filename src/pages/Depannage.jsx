import { useState } from "react";
import { useLang } from "../i18n.jsx";
import { depStore } from "../admin/store.js";

export default function Depannage() {
  const { t } = useLang();
  const [form, setForm] = useState({
    name: "",
    phone: "",
    plate: "",
    problem: "battery",
    location: "",
    notes: "",
  });
  const [sent, setSent] = useState(false);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = (e) => {
    e.preventDefault();
    depStore.add(form);
    setSent(true);
    setForm({
      name: "",
      phone: "",
      plate: "",
      problem: "battery",
      location: "",
      notes: "",
    });
  };

  const inputClass =
    "w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30 bg-white";

  const problems = [
    { id: "battery", key: "dep_p_battery" },
    { id: "tire", key: "dep_p_tire" },
    { id: "engine", key: "dep_p_engine" },
    { id: "other", key: "dep_p_other" },
  ];

  return (
    <>
      <section className="bg-gradient-to-br from-navy-900 via-navy-800 to-purple-900 text-white">
        <div className="container-x py-16 text-center">
          <h1 className="font-serif text-3xl md:text-5xl">{t("dep_title")}</h1>
          <p className="mt-2 text-blue-100">{t("dep_sub")}</p>
        </div>
      </section>

      <section className="bg-gray-50">
        <div className="container-x py-16 grid lg:grid-cols-5 gap-10 items-start">
          {/* Form on the left */}
          <form
            onSubmit={onSubmit}
            className="lg:col-span-3 bg-white rounded-2xl border border-gray-100 shadow-md p-6 md:p-8 space-y-5"
          >
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  {t("dep_full_name")}
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
                  {t("dep_phone")}
                </label>
                <input
                  type="tel"
                  name="phone"
                  required
                  value={form.phone}
                  onChange={onChange}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("dep_plate")}
              </label>
              <input
                name="plate"
                required
                value={form.plate}
                onChange={onChange}
                className={inputClass}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-2">
                {t("dep_problem")}
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {problems.map((p) => (
                  <label
                    key={p.id}
                    className={`cursor-pointer rounded-md border px-3 py-2 text-sm text-center transition ${
                      form.problem === p.id
                        ? "bg-navy-900 text-white border-navy-900"
                        : "bg-white text-gray-700 border-gray-200 hover:border-navy-900/40"
                    }`}
                  >
                    <input
                      type="radio"
                      name="problem"
                      value={p.id}
                      checked={form.problem === p.id}
                      onChange={onChange}
                      className="sr-only"
                    />
                    {t(p.key)}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("dep_location")}
              </label>
              <input
                name="location"
                required
                value={form.location}
                onChange={onChange}
                className={inputClass}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("dep_notes")}
              </label>
              <textarea
                name="notes"
                rows={3}
                value={form.notes}
                onChange={onChange}
                className={inputClass}
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-md bg-navy-900 text-white font-semibold py-3 hover:bg-navy-800 transition"
            >
              {t("dep_submit")}
            </button>

            {sent && (
              <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-md p-3">
                ✓ {t("dep_submit")} — OK
              </p>
            )}
          </form>

          {/* Visual on the right */}
          <aside className="lg:col-span-2 lg:sticky lg:top-24 space-y-4">
            <div className="rounded-2xl bg-white border border-gray-100 shadow-md overflow-hidden">
              <div className="aspect-square bg-gray-50 grid place-items-center p-8">
                <img
                  src="/photo_2026-04-28_11-24-12.jpg"
                  alt="Dépannage"
                  className="w-full h-full object-contain"
                  loading="lazy"
                />
              </div>
              <div className="p-5 text-center border-t border-gray-100">
                <h3 className="font-serif text-xl text-navy-900">
                  {t("dep_title")}
                </h3>
                <p className="mt-1 text-sm text-gray-600">{t("about_phone")}</p>
              </div>
            </div>
          </aside>
        </div>
      </section>
    </>
  );
}
