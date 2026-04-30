import { createContext, useContext, useEffect, useMemo, useState } from "react";
import fr from "./locales/fr.js";
import ar from "./locales/ar.js";
import en from "./locales/en.js";

const dictionaries = { fr, ar, en };
const LangContext = createContext(null);

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "fr");

  useEffect(() => {
    localStorage.setItem("lang", lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);

  const value = useMemo(() => {
    const t = (key) => {
      const d = dictionaries[lang] || dictionaries.fr;
      return d[key] ?? dictionaries.fr[key] ?? key;
    };
    return { lang, setLang, t, isRTL: lang === "ar" };
  }, [lang]);

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export const useLang = () => {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error("useLang must be used inside LanguageProvider");
  return ctx;
};
