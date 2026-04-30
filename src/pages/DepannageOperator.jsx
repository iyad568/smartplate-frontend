import { useState } from "react";
import { useLang } from "../i18n.jsx";
import { depStore } from "../admin/store.js";
import {
  OperatorShell,
  StatusBadge,
  StatusSelect,
  formatDate,
} from "../admin/AdminLayout.jsx";

export default function DepannageOperator() {
  const { t } = useLang();
  const [items, setItems] = useState(() => depStore.list());
  const [filter, setFilter] = useState("all");

  const refresh = () => setItems(depStore.list());

  const updateStatus = (id, status) => {
    depStore.update(id, { status });
    refresh();
  };

  const remove = (id) => {
    if (!confirm(t("admin_confirm_delete"))) return;
    depStore.remove(id);
    refresh();
  };

  const filtered =
    filter === "all" ? items : items.filter((i) => i.status === filter);

  const problemLabel = (p) => {
    const map = {
      battery: t("dep_p_battery"),
      tire: t("dep_p_tire"),
      engine: t("dep_p_engine"),
      other: t("dep_p_other"),
    };
    return map[p] || p;
  };

  return (
    <OperatorShell role="depannage">
      <div className="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden">
        <header className="p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-gray-100">
          <div>
            <h2 className="font-serif text-xl text-navy-900">
              {t("admin_dep_title")}
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              {items.length} {t("admin_total")}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="rounded-md border border-gray-200 px-3 py-2 text-sm"
            >
              <option value="all">{t("admin_filter_all")}</option>
              <option value="pending">{t("admin_status_pending")}</option>
              <option value="in_progress">{t("admin_status_in_progress")}</option>
              <option value="resolved">{t("admin_status_resolved")}</option>
            </select>
            <button
              onClick={refresh}
              className="rounded-md border border-gray-200 px-3 py-2 text-sm hover:bg-gray-50"
            >
              ↻
            </button>
          </div>
        </header>

        {filtered.length === 0 ? (
          <div className="p-10 text-center text-gray-500 text-sm">
            {t("admin_empty")}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="text-start p-3">{t("admin_col_date")}</th>
                  <th className="text-start p-3">{t("dep_full_name")}</th>
                  <th className="text-start p-3">{t("dep_phone")}</th>
                  <th className="text-start p-3">{t("dep_plate")}</th>
                  <th className="text-start p-3">{t("dep_problem")}</th>
                  <th className="text-start p-3">{t("dep_location")}</th>
                  <th className="text-start p-3">{t("dep_notes")}</th>
                  <th className="text-start p-3">{t("admin_col_status")}</th>
                  <th className="text-start p-3">{t("admin_col_actions")}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((i) => (
                  <tr key={i.id} className="border-t border-gray-100 align-top">
                    <td className="p-3 text-xs text-gray-500 whitespace-nowrap">
                      {formatDate(i.createdAt)}
                    </td>
                    <td className="p-3 font-medium text-navy-900">{i.name}</td>
                    <td className="p-3 text-gray-700">
                      <a
                        href={`tel:${i.phone}`}
                        className="hover:underline text-navy-900"
                      >
                        {i.phone}
                      </a>
                    </td>
                    <td className="p-3">
                      <span className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono">
                        {i.plate}
                      </span>
                    </td>
                    <td className="p-3 text-gray-700">
                      {problemLabel(i.problem)}
                    </td>
                    <td className="p-3 text-gray-700 text-xs">{i.location}</td>
                    <td className="p-3 text-gray-600 text-xs max-w-xs">
                      {i.notes || "—"}
                    </td>
                    <td className="p-3">
                      <StatusBadge status={i.status} />
                    </td>
                    <td className="p-3">
                      <div className="flex flex-col gap-2">
                        <StatusSelect
                          value={i.status}
                          onChange={(s) => updateStatus(i.id, s)}
                        />
                        <button
                          onClick={() => remove(i.id)}
                          className="text-xs text-red-600 hover:underline self-start"
                        >
                          {t("admin_delete")}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </OperatorShell>
  );
}
