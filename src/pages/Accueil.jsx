import { useLang } from "../i18n.jsx";

export default function Accueil() {
  const { t } = useLang();

  return (
    <div>
      {/* Hero */}
      <section className="relative bg-[#0b0f1c] text-white overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_50%_50%,#1f3b6e_0%,transparent_60%)]"
        />
        <div
          aria-hidden
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "linear-gradient(transparent 95%, rgba(255,255,255,.15) 95%), linear-gradient(90deg, transparent 95%, rgba(255,255,255,.15) 95%)",
            backgroundSize: "40px 40px",
          }}
        />
        <div className="container-x relative z-10 py-24 md:py-32 text-center">
          <h1 className="font-serif text-4xl md:text-6xl tracking-wide">
            {t("home_brand")}
          </h1>
          <p className="mt-4 text-lg md:text-xl text-gray-200">
            {t("home_tagline")}
          </p>
          <p className="mt-2 text-sm md:text-base text-gray-300">
            {t("home_subtagline")}
          </p>
          <p className="mt-8 text-sm italic text-gray-300">{t("home_quote")}</p>
        </div>
      </section>

      {/* Welcome / Intro */}
      <section className="bg-gray-50">
        <div className="container-x py-16 grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h2 className="font-serif text-3xl md:text-4xl text-navy-900">
              {t("home_intro_title")}
            </h2>
            <p className="mt-4 text-gray-700">{t("home_intro_p1")}</p>
            <p className="mt-3 text-gray-700">{t("home_intro_p2")}</p>
            <p className="mt-3 text-gray-700">{t("home_intro_p3")}</p>
          </div>

          <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
            <div className="aspect-[3/2] overflow-hidden bg-gray-100">
              <img
                src="/photo_2026-04-28_11-22-43.jpg"
                alt="Officer scanning Smart Plate with QR code and RFID"
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
            <div className="p-5 grid grid-cols-3 text-center text-xs text-gray-600 border-t border-gray-100">
              <div>
                <div className="text-2xl font-bold text-navy-900">10k+</div>
                <div>plates</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-navy-900">48</div>
                <div>wilayas</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-navy-900">24/7</div>
                <div>support</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* New generation — text left, photo right */}
      <section className="bg-white">
        <div className="container-x py-16 grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h2 className="font-serif text-3xl md:text-4xl text-navy-900">
              {t("home_gen_title")}
            </h2>
            <p className="mt-4 text-gray-700">{t("home_gen_p1")}</p>
          </div>

          <div className="rounded-xl bg-white shadow-sm border border-gray-100 overflow-hidden">
            <div className="aspect-[3/2] overflow-hidden bg-gray-100">
              <img
                src="/photo_2026-04-28_11-24-03.jpg"
                alt="Smart Plate DZ on a real vehicle"
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          </div>
        </div>

        {/* Bullets below */}
        <div className="container-x pb-16">
          <ul className="grid md:grid-cols-3 gap-6">
            {[t("home_gen_b1"), t("home_gen_b2"), t("home_gen_b3")].map(
              (item, i) => (
                <li
                  key={i}
                  className="rounded-xl border border-gray-100 bg-gray-50 p-6 text-gray-700"
                >
                  <div className="w-9 h-9 rounded-full bg-navy-900 text-white grid place-items-center font-bold mb-3">
                    {i + 1}
                  </div>
                  {item}
                </li>
              )
            )}
          </ul>
        </div>
      </section>

      {/* Reviews */}
      <section className="bg-gray-50">
        <div className="container-x py-16">
          <h2 className="font-serif text-3xl md:text-4xl text-navy-900 text-center">
            {t("reviews_title")}
          </h2>
          <p className="mt-2 text-gray-600 text-center">{t("reviews_sub")}</p>

          <div className="mt-10 grid md:grid-cols-2 gap-6">
            {[
              {
                text: t("review1_text"),
                name: t("review1_name"),
                city: t("review1_city"),
              },
              {
                text: t("review2_text"),
                name: t("review2_name"),
                city: t("review2_city"),
              },
            ].map((r, i) => (
              <article
                key={i}
                className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm"
              >
                <div className="text-yellow-500" aria-label="5 étoiles">
                  ★★★★★
                </div>
                <p className="mt-3 text-gray-700">{r.text}</p>
                <p className="mt-4 text-sm font-semibold text-navy-900">
                  {r.name}
                </p>
                <p className="text-xs text-gray-500">{r.city}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
