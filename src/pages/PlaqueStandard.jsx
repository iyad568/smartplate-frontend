import { useState } from "react";
import { useLang } from "../i18n.jsx";

export default function PlaqueStandard() {
  const { t } = useLang();
  const [form, setForm] = useState({
    name: "",
    first: "",
    phone: "",
    email: "",
    cni: "",
    address: "",
    chassis: "",
    type: "",
    brand: "",
    plate: "",
    power: "essence",
  });

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = (action) => (e) => {
    e.preventDefault();
    alert(`${action}: ${form.name} ${form.first}`);
  };

  const inputClass =
    "w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30 bg-white";

  return (
    <section className="bg-gradient-to-br from-gray-50 via-purple-100/40 to-gray-100">
      <div className="container-x py-16 grid lg:grid-cols-5 gap-10 items-start">
        {/* Form on the left (3 cols) */}
        <form
          onSubmit={submit(t("ps_register"))}
          className="lg:col-span-3 bg-white rounded-2xl border border-gray-100 shadow-md p-6 md:p-8 space-y-5"
        >
          <h1 className="font-serif text-2xl md:text-3xl text-navy-900 mb-2">
            {t("ps_personal")}
          </h1>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_name")}
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
                {t("ps_first")}
              </label>
              <input
                name="first"
                required
                value={form.first}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_phone")}
              </label>
              <input
                name="phone"
                type="tel"
                value={form.phone}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_email")}
              </label>
              <input
                name="email"
                type="email"
                required
                value={form.email}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_cni")}
              </label>
              <input
                name="cni"
                required
                value={form.cni}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_address")}
              </label>
              <input
                name="address"
                required
                value={form.address}
                onChange={onChange}
                className={inputClass}
              />
            </div>
          </div>

          <h2 className="font-serif text-2xl text-navy-900 pt-4 border-t border-gray-200">
            {t("ps_vehicle")}
          </h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_chassis")}
              </label>
              <input
                name="chassis"
                required
                value={form.chassis}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_type")}
              </label>
              <input
                name="type"
                required
                value={form.type}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_brand")}
              </label>
              <input
                name="brand"
                required
                value={form.brand}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_plate_number")}
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
            <label className="block text-xs font-medium text-gray-600 mb-2">
              {t("ps_power")}
            </label>
            <div className="flex flex-wrap gap-4 text-sm">
              {["essence", "diesel", "gpl", "hybride"].map((p) => (
                <label key={p} className="inline-flex items-center gap-2">
                  <input
                    type="radio"
                    name="power"
                    value={p}
                    checked={form.power === p}
                    onChange={onChange}
                  />
                  {t(`ps_${p}`)}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {t("ps_attach_card")}
            </label>
            <input
              type="file"
              accept="image/*,.pdf"
              className="block w-full text-sm text-gray-700 file:mr-3 file:rounded-md file:border-0 file:bg-navy-900 file:text-white file:px-4 file:py-2 file:cursor-pointer hover:file:bg-navy-800"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-200">
            <div className="font-semibold text-navy-900">{t("ps_price")}</div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={submit(t("ps_register"))}
                className="rounded-md bg-gray-700 text-white px-5 py-2 text-sm font-medium hover:bg-gray-800 transition"
              >
                {t("ps_register")}
              </button>
              <button
                type="submit"
                onClick={submit(t("ps_pay"))}
                className="rounded-md bg-navy-900 text-white px-5 py-2 text-sm font-medium hover:bg-navy-800 transition"
              >
                {t("ps_pay")}
              </button>
            </div>
          </div>
        </form>

        {/* Plate preview on the right (2 cols) */}
        <aside className="lg:col-span-2 lg:sticky lg:top-24 space-y-4">
          <div className="rounded-2xl bg-white border border-gray-100 shadow-md overflow-hidden">
            <img
              src="/photo_2026-04-28_11-22-53.jpg"
              alt="Plaque d'immatriculation Standard"
              className="w-full h-auto object-cover"
              loading="lazy"
            />
            <div className="p-5 text-center">
              <h3 className="font-serif text-xl text-navy-900">
                {t("product_standard")}
              </h3>
              <p className="mt-1 text-sm text-gray-600">{t("ps_price")}</p>
            </div>
          </div>
          <div className="rounded-xl bg-navy-900/5 border border-navy-900/10 p-4 text-sm text-gray-700 text-center">
            {t("smartsticks_inline")} — 1000 {t("dz")}
          </div>
        </aside>
      </div>
    </section>
  );
}
