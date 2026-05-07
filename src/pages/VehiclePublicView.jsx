import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiService } from "../services/api.js";

function Field({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </span>
      <span className="text-sm font-semibold text-gray-900">{value}</span>
    </div>
  );
}

function DocLink({ label, url }) {
  if (!url) return null;
  const isPdf = url.toLowerCase().endsWith(".pdf");
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 hover:bg-blue-50 transition"
    >
      {isPdf ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
            stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
          <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2" />
          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
          <path d="M21 15l-5-5L5 21" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        </svg>
      )}
      {label}
    </a>
  );
}

export default function VehiclePublicView() {
  const { qrCode } = useParams();
  const navigate = useNavigate();
  const [car, setCar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiService.getPublicVehicle(qrCode)
      .then(setCar)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [qrCode]);

  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center text-gray-500">
        Chargement…
      </div>
    );
  }

  if (error || !car) {
    return (
      <div className="min-h-screen grid place-items-center text-center p-8">
        <div>
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 grid place-items-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-red-500">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <p className="text-gray-700 font-medium mb-1">Véhicule introuvable</p>
          <p className="text-gray-400 text-sm mb-4">{error}</p>
          <button onClick={() => navigate("/")}
            className="rounded-md bg-[#0b1d3a] text-white px-4 py-2 text-sm hover:opacity-90 transition">
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  const fuelLabel = {
    essence: "Essence", diesel: "Diesel", gpl: "GPL",
    hybride: "Hybride", electrique: "Électrique",
  };

  const hasOwner = car.owner_name || car.owner_first_name || car.cni_number || car.owner_phone;
  const hasDocs = car.assurance_paper_url || car.license_url || car.cart_grise_url ||
    car.vignette_url || car.controle_technique_url || car.plate_photo_url;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-gray-100 py-10 px-4">
      <div className="max-w-lg mx-auto space-y-5">

        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-white border border-gray-200 px-4 py-1.5 shadow-sm text-xs font-medium text-gray-600 mb-4">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="text-green-500">
              <path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6l8-3z" />
            </svg>
            Vérifié · SmartPlate DZ
          </div>
          <h1 className="font-serif text-2xl text-gray-900">Informations du véhicule</h1>
        </div>

        {/* Plate photo */}
        {car.plate_photo_url && (
          <div className="rounded-xl overflow-hidden shadow-md border border-gray-200">
            <img src={car.plate_photo_url} alt="Photo de la plaque"
              className="w-full h-44 object-cover" />
          </div>
        )}

        {/* Vehicle info */}
        <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
          <div className="bg-[#0b1d3a] text-white px-5 py-3 flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="7" width="18" height="10" rx="1" stroke="currentColor" strokeWidth="2" />
              <path d="M7 11h10M7 14h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            <span className="font-semibold text-sm">Informations véhicule</span>
          </div>
          <div className="p-5 grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">
                Numéro de plaque
              </span>
              <div className="mt-1 inline-flex items-center rounded-lg bg-[#0b1d3a] text-white px-4 py-2 font-extrabold text-lg tracking-widest">
                {car.plate_number}
              </div>
            </div>
            <Field label="Marque" value={car.vehicle_brand} />
            <Field label="Type" value={car.vehicle_type} />
            <Field label="Motorisation" value={fuelLabel[car.power_type] || car.power_type} />
            <Field label="N° châssis" value={car.chassis_number} />
            <div className="flex flex-col gap-0.5">
              <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Statut</span>
              <span className={`inline-flex w-fit items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold
                ${car.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${car.is_active ? "bg-green-500" : "bg-red-500"}`} />
                {car.is_active ? "Actif" : "Inactif"}
              </span>
            </div>
          </div>
        </div>

        {/* Owner info */}
        {hasOwner && (
          <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
            <div className="bg-[#0b1d3a] text-white px-5 py-3 flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span className="font-semibold text-sm">Informations du propriétaire</span>
            </div>
            <div className="p-5 grid grid-cols-2 gap-4">
              <Field label="Nom" value={car.owner_name} />
              <Field label="Prénom" value={car.owner_first_name} />
              <Field label="N° CIN" value={car.cni_number} />
              <Field label="Téléphone" value={car.owner_phone} />
              <div className="col-span-2"><Field label="Email" value={car.owner_email} /></div>
              <div className="col-span-2"><Field label="Adresse" value={car.owner_address} /></div>
            </div>
          </div>
        )}

        {/* Documents */}
        {hasDocs && (
          <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
            <div className="bg-[#0b1d3a] text-white px-5 py-3 flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
                  stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
              </svg>
              <span className="font-semibold text-sm">Documents</span>
            </div>
            <div className="p-4 grid grid-cols-2 gap-2">
              <DocLink label="Photo plaque" url={car.plate_photo_url} />
              <DocLink label="Assurance" url={car.assurance_paper_url} />
              <DocLink label="Permis" url={car.license_url} />
              <DocLink label="Carte grise" url={car.cart_grise_url} />
              <DocLink label="Vignette" url={car.vignette_url} />
              <DocLink label="Contrôle technique" url={car.controle_technique_url} />
            </div>
          </div>
        )}

        <p className="text-center text-xs text-gray-400 pb-4">
          VÉRIFIABLE SUR SMARTPLATE.DZ · SmartPlate DZ
        </p>
      </div>
    </div>
  );
}
