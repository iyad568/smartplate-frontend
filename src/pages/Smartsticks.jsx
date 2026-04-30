import { useLang } from "../i18n.jsx";

export default function Smartsticks() {
  const { t } = useLang();

  return (
    <>
      <section className="relative overflow-hidden bg-[#0a0f1c] text-white">
        <div
          aria-hidden
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "radial-gradient(rgba(80,180,255,.25) 1px, transparent 1px)",
            backgroundSize: "22px 22px",
          }}
        />
        <div className="container-x relative z-10 py-24 md:py-32 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="font-serif text-4xl md:text-5xl leading-tight">
              {t("ss_title")}
            </h1>
            <p className="mt-4 text-lg text-gray-200">{t("ss_sub")}</p>
            <div className="mt-8 inline-flex items-baseline gap-2 rounded-full bg-white/10 border border-white/20 px-5 py-2">
              <span className="text-sm uppercase tracking-widest text-gray-300">
                {t("price_label")}
              </span>
              <span className="text-xl font-semibold">{t("ss_price")}</span>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-white">
              <img
                src="/photo_2026-04-28_11-22-48.jpg"
                alt="SMARTSTIX vignette de sécurité avec puce RFID et QR code"
                className="w-full h-auto object-cover"
                loading="lazy"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white">
        <div className="container-x py-16 grid md:grid-cols-2 gap-10">
          <p className="text-gray-700 leading-relaxed">{t("ss_p1")}</p>
          <p className="text-gray-700 leading-relaxed">{t("ss_p2")}</p>
        </div>
      </section>
    </>
  );
}
