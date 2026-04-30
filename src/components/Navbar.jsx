import { useState } from "react";
import { NavLink, Link } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import Logo from "./Logo.jsx";
import LanguageSwitcher from "./LanguageSwitcher.jsx";

export default function Navbar() {
  const { t } = useLang();
  const [open, setOpen] = useState(false);

  const items = [
    { to: "/se-connecter", label: t("nav_login") },
    { to: "/", label: t("nav_home"), end: true },
    { to: "/produits", label: t("nav_products") },
    { to: "/services", label: t("nav_services") },
    { to: "/smartsticks", label: t("nav_smartsticks") },
    { to: "/securite", label: t("nav_security") },
    { to: "/a-propos", label: t("nav_about") },
    { to: "/bienvenue", label: t("nav_welcome") },
  ];

  return (
    <header className="bg-gray-100 border-b border-gray-200">
      <div className="container-x flex items-center justify-between py-4 gap-4">
        <Link to="/" className="shrink-0">
          <Logo />
        </Link>

        <nav className="hidden lg:flex items-center gap-6 flex-1 justify-center">
          {items.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end={it.end}
              className={({ isActive }) =>
                `nav-link ${isActive ? "nav-link-active" : ""}`
              }
            >
              {it.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden lg:block">
          <LanguageSwitcher />
        </div>

        <button
          className="lg:hidden p-2 text-navy-900"
          aria-label="menu"
          onClick={() => setOpen((o) => !o)}
        >
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <path d="M3 6h16M3 11h16M3 16h16" stroke="currentColor" strokeWidth="2" />
          </svg>
        </button>
      </div>

      {open && (
        <div className="lg:hidden border-t border-gray-200 bg-white">
          <ul className="container-x py-3 space-y-1">
            {items.map((it) => (
              <li key={it.to}>
                <NavLink
                  to={it.to}
                  end={it.end}
                  className={({ isActive }) =>
                    `block py-2 nav-link ${isActive ? "nav-link-active" : ""}`
                  }
                  onClick={() => setOpen(false)}
                >
                  {it.label}
                </NavLink>
              </li>
            ))}
            <li className="pt-2">
              <LanguageSwitcher />
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
