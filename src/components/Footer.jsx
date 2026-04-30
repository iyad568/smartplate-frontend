import { useLang } from "../i18n.jsx";

export default function Footer() {
  const { t } = useLang();

  return (
    <footer className="relative overflow-hidden bg-gradient-to-br from-[#0b1d3a] via-[#1a1135] to-[#3a0d4d] text-white">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-20 left-1/2 h-64 w-64 rounded-full bg-blue-500/40 blur-3xl"
      />
      <div className="container-x relative z-10 py-12 grid grid-cols-1 md:grid-cols-3 gap-10">
        <div>
          <h4 className="text-lg font-semibold mb-3">{t("foot_address_label")}</h4>
          <p className="text-sm text-gray-200">{t("foot_address")}</p>
        </div>

        <div>
          <h4 className="text-lg font-semibold mb-3">{t("foot_contacts_label")}</h4>
          <p className="text-sm text-gray-200">
            <a href={`tel:${t("foot_phone")}`} className="hover:underline">
              {t("foot_phone")}
            </a>
          </p>
          <p className="text-sm text-gray-200 mt-1">
            <a href={`mailto:${t("foot_email")}`} className="hover:underline">
              {t("foot_email")}
            </a>
          </p>
        </div>

        <div>
          <h4 className="text-lg font-semibold mb-3">{t("foot_news_title")}</h4>
          <form
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              alert(t("foot_subscribe") + " ✓");
            }}
          >
            <label className="text-xs text-gray-300">{t("foot_news_email")}</label>
            <input
              type="email"
              required
              placeholder={t("foot_news_placeholder")}
              className="rounded-md bg-white/95 text-gray-900 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-white/60"
            />
            <button
              type="submit"
              className="self-start mt-1 inline-flex items-center justify-center bg-black text-white px-5 py-2 text-sm font-medium rounded-md hover:bg-black/80 transition"
            >
              {t("foot_subscribe")}
            </button>
          </form>
        </div>
      </div>

      <div className="relative z-10 border-t border-white/10">
        <div className="container-x py-4 text-xs text-gray-300">
          {t("foot_copy")}
        </div>
      </div>
    </footer>
  );
}
