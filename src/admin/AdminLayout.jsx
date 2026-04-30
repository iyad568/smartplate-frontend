import { Navigate, useLocation, NavLink, useNavigate } from "react-router-dom";
import { adminAuth, userStore } from "./store.js";
import { useLang } from "../i18n.jsx";

export function RequireAdmin({ children }) {
  const location = useLocation();
  if (!adminAuth.isLoggedIn()) {
    return (
      <Navigate
        to="/admin"
        state={{ from: location.pathname }}
        replace
      />
    );
  }
  return children;
}

export function RequireOperator({ children, allowedRoles }) {
  const location = useLocation();
  const user = userStore.getCurrentUser();
  
  if (!user || !allowedRoles.includes(user.role)) {
    return (
      <Navigate
        to="/se-connecter"
        state={{ from: location.pathname }}
        replace
      />
    );
  }
  return children;
}

export function RequireUser({ children }) {
  const location = useLocation();
  const user = userStore.getCurrentUser();
  
  if (!user) {
    return (
      <Navigate
        to="/se-connecter"
        state={{ from: location.pathname }}
        replace
      />
    );
  }
  return children;
}

export function AdminShell({ children }) {
  const { t } = useLang();
  const navigate = useNavigate();
  const email = adminAuth.email();

  const logout = () => {
    adminAuth.logout();
    navigate("/admin", { replace: true });
  };

  return (
    <section className="bg-gray-50 min-h-[80vh]">
      <div className="container-x py-8">
        <header className="rounded-2xl bg-gradient-to-r from-navy-900 to-navy-800 text-white p-5 md:p-6 shadow-md flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-blue-200">
              {t("admin_title")}
            </p>
            <h1 className="font-serif text-2xl md:text-3xl mt-1">
              {t("admin_dashboard")}
            </h1>
            {email && (
              <p className="text-xs text-blue-100 mt-1">{email}</p>
            )}
          </div>
          <button
            onClick={logout}
            className="self-start md:self-auto inline-flex items-center gap-2 rounded-md border border-white/30 px-4 py-2 text-sm hover:bg-white/10 transition"
          >
            {t("admin_logout")}
          </button>
        </header>

        <nav className="mt-6 flex gap-2 border-b border-gray-200">
          {[
            { to: "/admin/sos", label: t("admin_tab_sos") },
            { to: "/admin/depannage", label: t("admin_tab_dep") },
          ].map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                `px-4 py-2 text-sm font-medium rounded-t-md transition ${
                  isActive
                    ? "bg-white text-navy-900 border-x border-t border-gray-200"
                    : "text-gray-600 hover:text-navy-900"
                }`
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-6">{children}</div>
      </div>
    </section>
  );
}

export function OperatorShell({ children, role }) {
  const { t } = useLang();
  const navigate = useNavigate();
  const user = userStore.getCurrentUser();

  const logout = () => {
    userStore.logout();
    navigate("/se-connecter", { replace: true });
  };

  const roleLabel = role === "sos" ? t("admin_tab_sos") : t("admin_tab_dep");

  return (
    <section className="bg-gray-50 min-h-[80vh]">
      <div className="container-x py-8">
        <header className="rounded-2xl bg-gradient-to-r from-navy-900 to-navy-800 text-white p-5 md:p-6 shadow-md flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-blue-200">
              {roleLabel}
            </p>
            <h1 className="font-serif text-2xl md:text-3xl mt-1">
              {t("admin_dashboard")}
            </h1>
            {user && (
              <p className="text-xs text-blue-100 mt-1">{user.fullname || user.email}</p>
            )}
          </div>
          <button
            onClick={logout}
            className="self-start md:self-auto inline-flex items-center gap-2 rounded-md border border-white/30 px-4 py-2 text-sm hover:bg-white/10 transition"
          >
            {t("admin_logout")}
          </button>
        </header>

        <div className="mt-6">{children}</div>
      </div>
    </section>
  );
}

const STATUSES = ["pending", "in_progress", "resolved"];

export function StatusBadge({ status }) {
  const { t } = useLang();
  const colors = {
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    in_progress: "bg-blue-100 text-blue-800 border-blue-200",
    resolved: "bg-green-100 text-green-800 border-green-200",
  };
  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full border ${
        colors[status] || colors.pending
      }`}
    >
      {t(`admin_status_${status}`) || status}
    </span>
  );
}

export function StatusSelect({ value, onChange }) {
  const { t } = useLang();
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs"
    >
      {STATUSES.map((s) => (
        <option key={s} value={s}>
          {t(`admin_status_${s}`) || s}
        </option>
      ))}
    </select>
  );
}

export function formatDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}
