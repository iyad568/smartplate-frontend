import { useLang } from "../i18n.jsx";

export default function TopBanner() {
  const { t } = useLang();
  return (
    <div className="bg-navy-900 text-white text-center py-2 px-4">
      <div className="text-sm md:text-base font-medium" dir="rtl">
        {t("govLine1")}
      </div>
      <div className="text-xs md:text-sm opacity-90 mt-1" dir="rtl">
        {t("govLine2")}
      </div>
    </div>
  );
}
