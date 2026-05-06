import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api.js";

export default function ImprimerLicence() {
  const navigate = useNavigate();
  const [car, setCar] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiService.getUserCars();
        const list = res.cars || [];
        if (list.length > 0) {
          const savedId = localStorage.getItem("selected_car_id");
          setCar((savedId && list.find((c) => c.id === savedId)) || list[0]);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const fmt = (iso) =>
    iso ? new Date(iso).toLocaleDateString("fr-FR") : "—";

  const serial = car
    ? `SP-${new Date(car.created_at).getFullYear()}-${car.id.slice(-6).toUpperCase()}`
    : "—";

  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center text-gray-500">
        Chargement...
      </div>
    );
  }

  if (!car) {
    return (
      <div className="min-h-screen grid place-items-center text-center p-8">
        <div>
          <p className="text-gray-600 mb-4">Aucun véhicule trouvé.</p>
          <button
            onClick={() => navigate("/bienvenue")}
            className="rounded-md bg-navy-900 text-white px-5 py-2 text-sm hover:bg-navy-800 transition"
          >
            Retour
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-10 print:bg-white print:py-0">
      {/* Toolbar — hidden when printing */}
      <div className="mb-6 flex gap-3 print:hidden">
        <button
          onClick={() => navigate("/bienvenue")}
          className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M5 12l7-7M5 12l7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Retour
        </button>
        <button
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 rounded-md bg-navy-900 text-white px-5 py-2 text-sm font-medium hover:bg-navy-800 transition"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <rect x="6" y="3" width="12" height="6" stroke="currentColor" strokeWidth="2" />
            <rect x="3" y="9" width="18" height="9" rx="1" stroke="currentColor" strokeWidth="2" />
            <rect x="7" y="14" width="10" height="6" stroke="currentColor" strokeWidth="2" />
          </svg>
          Imprimer
        </button>
      </div>

      {/* License card — lili.png template with overlaid real data */}
      <div
        className="relative shadow-xl print:shadow-none"
        style={{ width: 480, height: 620 }}
      >
        {/* Background template */}
        <img
          src="/lili.png"
          alt="Licence template"
          className="absolute inset-0 w-full h-full"
          draggable={false}
        />

        {/* ── Plate number — centred in the plate rectangle ── */}
        <span
          className="absolute font-extrabold text-white tracking-widest"
          style={{ left: "16%", top: "31%", fontSize: 22, letterSpacing: 4 }}
        >
          {car.plate_number || "—"}
        </span>

        {/* ── Nom — right column, same row as "Nom" label ── */}
        <span
          className="absolute font-bold text-gray-900 uppercase"
          style={{ left: "65%", top: "46%", fontSize: 11 }}
        >
          {car.owner_name || "—"}
        </span>

        {/* ── Prénom — right column, row 2 ─────────────────── */}
        <span
          className="absolute font-semibold text-gray-900"
          style={{ left: "65%", top: "52%", fontSize: 11 }}
        >
          {car.owner_first_name || "—"}
        </span>

        {/* ── CIN — right column, row 3 ────────────────────── */}
        <span
          className="absolute font-semibold text-gray-900"
          style={{ left: "65%", top: "58%", fontSize: 11 }}
        >
          {car.cni_number || "—"}
        </span>

        {/* ── Type — right column, row 4 ("Standard" spot) ─── */}
        <span
          className="absolute font-semibold text-gray-900"
          style={{ left: "65%", top: "64%", fontSize: 11 }}
        >
          {car.vehicle_type || "Standard"}
        </span>

        {/* ── Numéro de série — after left label, row 5 ─────── */}
        <span
          className="absolute font-semibold text-gray-900"
          style={{ left: "38%", top: "69%", fontSize: 11 }}
        >
          {serial}
        </span>

        {/* ── Date d'achat — after left label, row 6 ──────── */}
        <span
          className="absolute font-semibold text-gray-900"
          style={{ left: "31%", top: "75%", fontSize: 11 }}
        >
          {fmt(car.created_at)}
        </span>
      </div>
    </div>
  );
}
