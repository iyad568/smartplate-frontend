import { useState } from "react";
import { useLang } from "../i18n.jsx";

export default function APropos() {
  const { t } = useLang();
  const [form, setForm] = useState({ first: "", email: "", message: "" });
  const [sent, setSent] = useState(false);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  const onSubmit = (e) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <>
      <section className="bg-gradient-to-br from-[#bdaee0] via-[#a072c8] to-[#7e3db0] text-white">
        <div className="container-x py-20 text-center">
          <h1 className="font-serif text-4xl md:text-5xl">{t("about_title")}</h1>
          <p className="mt-3 max-w-2xl mx-auto text-white/90">
            {t("about_sub")}
          </p>
        </div>
      </section>

      <section className="bg-white">
        <div className="container-x py-16 grid lg:grid-cols-2 gap-12">
          <div>
            <div className="grid sm:grid-cols-2 gap-4 mb-8">
              <div className="rounded-xl border border-gray-100 p-5">
                <h3 className="font-semibold text-navy-900">
                  {t("about_assistance")}
                </h3>
                <p className="mt-2 text-gray-700 text-sm">{t("about_phone")}</p>
              </div>
              <div className="rounded-xl border border-gray-100 p-5">
                <h3 className="font-semibold text-navy-900">
                  {t("about_support")}
                </h3>
                <p className="mt-2 text-gray-700 text-sm">{t("about_email")}</p>
              </div>
            </div>

            <form onSubmit={onSubmit} className="space-y-4">
              <input
                name="first"
                value={form.first}
                onChange={onChange}
                placeholder={t("form_first")}
                className="w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
              />
              <input
                name="email"
                type="email"
                required
                value={form.email}
                onChange={onChange}
                placeholder={t("form_email")}
                className="w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
              />
              <textarea
                name="message"
                rows={5}
                required
                value={form.message}
                onChange={onChange}
                placeholder={t("form_message")}
                className="w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
              />
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-md bg-navy-900 text-white px-6 py-3 font-medium hover:bg-navy-800 transition"
              >
                {t("form_submit")}
              </button>
              {sent && (
                <p className="text-sm text-green-600">✓ {t("form_submit")} — OK</p>
              )}
            </form>
          </div>

          <aside className="bg-gray-50 border border-gray-100 rounded-xl p-6">
            <h3 className="font-serif text-2xl text-navy-900">
              {t("about_gps")}
            </h3>
            <p className="mt-2 text-gray-700">{t("about_gps_text")}</p>

            <dl className="mt-6 space-y-4 text-sm">
              <div>
                <dt className="font-semibold text-navy-900">
                  {t("about_addr_label")}
                </dt>
                <dd className="text-gray-700">{t("about_addr_text")}</dd>
              </div>
              <div>
                <dt className="font-semibold text-navy-900">
                  {t("about_hours_label")}
                </dt>
                <dd className="text-gray-700">{t("about_hours_text")}</dd>
              </div>
            </dl>

            <div className="mt-6 rounded-lg overflow-hidden border border-gray-200 aspect-video">
              <iframe
                title="Map"
                src="https://www.openstreetmap.org/export/embed.html?bbox=2.7%2C36.4%2C3.0%2C36.6&amp;layer=mapnik"
                className="w-full h-full"
                loading="lazy"
              />
            </div>
          </aside>
        </div>
      </section>
    </>
  );
}
