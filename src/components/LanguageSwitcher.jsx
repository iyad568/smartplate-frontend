import { useState, useRef, useEffect } from "react";
import { useLang } from "../i18n.jsx";

const LANGS = [
  { code: "ar", label: "AR", name: "العربية" },
  { code: "en", label: "EN", name: "English" },
  { code: "fr", label: "FR", name: "Français" },
];

export default function LanguageSwitcher() {
  const { lang, setLang } = useLang();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const current = LANGS.find((l) => l.code === lang) || LANGS[2];

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 px-2 py-1 text-sm text-gray-700 hover:text-navy-900"
      >
        <span className="font-medium">{current.label}</span>
        <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden>
          <path d="M1 3l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" />
        </svg>
      </button>
      {open && (
        <ul className="absolute end-0 mt-1 w-32 bg-white border border-gray-200 rounded shadow-lg z-50">
          {LANGS.map((l) => (
            <li key={l.code}>
              <button
                onClick={() => {
                  setLang(l.code);
                  setOpen(false);
                }}
                className={`block w-full text-start px-3 py-1.5 text-sm hover:bg-gray-50 ${
                  l.code === lang ? "text-navy-900 font-semibold" : "text-gray-700"
                }`}
              >
                {l.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
