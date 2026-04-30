import { useLang } from "../i18n.jsx";

export default function Securite() {
  const { t } = useLang();

  return (
    <>
      <section className="relative overflow-hidden bg-blue-900 text-white">
        <img
          src="/photo_2026-04-28_11-24-08.jpg"
          alt=""
          aria-hidden
          className="absolute inset-0 w-full h-full object-cover opacity-50"
        />
        <div
          aria-hidden
          className="absolute inset-0 bg-gradient-to-br from-blue-900/80 via-blue-900/60 to-purple-900/70"
        />
        <div className="container-x relative z-10 py-24 text-center">
          <h1 className="font-serif text-4xl md:text-5xl">{t("sec_title")}</h1>
          <p className="mt-3 text-lg text-blue-100">{t("sec_sub")}</p>
        </div>
      </section>

      <section className="bg-white">
        <div className="container-x py-16 grid md:grid-cols-3 gap-6">
          {[
            { title: t("sec_smartcity"), text: t("sec_smartcity_text") },
            { title: t("sec_rfid"), text: t("ss_p2") },
            { title: t("sec_toll"), text: t("sec_toll_text") },
          ].map((c, i) => (
            <article
              key={i}
              className="rounded-xl border border-gray-100 bg-gray-50 p-6 hover:shadow-md transition"
            >
              <div className="w-10 h-10 rounded-lg bg-navy-900 text-white grid place-items-center mb-4 font-bold">
                {i + 1}
              </div>
              <h3 className="font-serif text-2xl text-navy-900">{c.title}</h3>
              <p className="mt-3 text-gray-700 text-sm leading-relaxed">
                {c.text}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-gradient-to-br from-navy-900 via-navy-800 to-purple-900 text-white">
        <div className="container-x py-12 text-center">
          <div className="inline-block">
            <div className="text-5xl font-serif">{t("sec_stat")}</div>
            <div className="text-sm tracking-widest uppercase mt-2 text-gray-200">
              {t("sec_stat_label")}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
