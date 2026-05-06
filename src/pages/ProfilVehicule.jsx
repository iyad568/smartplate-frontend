import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { apiService } from "../services/api.js";

function Field({ label, value }) {
  return (
    <div className="py-3 border-b border-gray-100 last:border-0">
      <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</dt>
      <dd className="mt-1 text-sm font-medium text-gray-900">
        {value ?? <span className="text-gray-400 italic">Non renseigné</span>}
      </dd>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
        <h3 className="font-serif text-lg text-navy-900">{title}</h3>
      </div>
      <dl className="px-6 py-2">{children}</dl>
    </div>
  );
}

const IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".gif", ".webp"];

function isImage(url) {
  if (!url) return false;
  const lower = url.toLowerCase().split("?")[0];
  return IMAGE_EXTS.some((ext) => lower.endsWith(ext));
}

function DocLink({ label, url }) {
  if (!url) return <Field label={label} value={null} />;
  return (
    <div className="py-3 border-b border-gray-100 last:border-0">
      <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">{label}</dt>
      <dd className="mt-1">
        {isImage(url) ? (
          <a href={url} target="_blank" rel="noopener noreferrer">
            <img
              src={url}
              alt={label}
              className="h-32 w-auto rounded-md border border-gray-200 object-cover hover:opacity-90 transition"
            />
          </a>
        ) : (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-navy-900 font-medium hover:underline"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Voir le document (PDF)
          </a>
        )}
      </dd>
    </div>
  );
}

const POWER_LABELS = {
  essence: "Essence",
  diesel: "Diesel",
  gpl: "GPL",
  hybride: "Hybride",
};

const STATUS_COLORS = {
  active: "bg-green-100 text-green-700",
  not_active: "bg-red-100 text-red-700",
};

export default function ProfilVehicule() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [cars, setCars] = useState([]);
  const [selectedCar, setSelectedCar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCars();
  }, []);

  const loadCars = async () => {
    try {
      const response = await apiService.getUserCars();
      const carList = response.cars || [];
      setCars(carList);

      if (carList.length > 0) {
        const savedId = localStorage.getItem("selected_car_id");
        const restored = savedId && carList.find((c) => c.id === savedId);
        setSelectedCar(restored || carList[0]);
      }
    } catch (err) {
      setError("Impossible de charger les données du véhicule.");
    } finally {
      setLoading(false);
    }
  };

  const handleCarChange = (carId) => {
    const car = cars.find((c) => c.id === carId);
    if (car) {
      setSelectedCar(car);
      localStorage.setItem("selected_car_id", car.id);
    }
  };

  const formatDate = (iso) =>
    iso ? new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" }) : null;

  if (loading) {
    return (
      <section className="bg-gray-50 min-h-[80vh] grid place-items-center">
        <div className="flex items-center gap-3 text-gray-500">
          <svg className="animate-spin" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
            <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" className="opacity-75" fill="currentColor" />
          </svg>
          Chargement du profil...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="bg-gray-50 min-h-[80vh] grid place-items-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={() => navigate("/bienvenue")} className="text-sm text-navy-900 underline">
            Retour au tableau de bord
          </button>
        </div>
      </section>
    );
  }

  if (!selectedCar) {
    return (
      <section className="bg-gray-50 min-h-[80vh] grid place-items-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Aucun véhicule enregistré.</p>
          <button
            onClick={() => navigate("/bienvenue")}
            className="rounded-md bg-navy-900 text-white px-5 py-2 text-sm hover:bg-navy-800 transition"
          >
            Ajouter un véhicule
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-gray-50 min-h-[80vh]">
      <div className="container-x py-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <button
              onClick={() => navigate("/bienvenue")}
              className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-2"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M19 12H5M5 12l7-7M5 12l7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Tableau de bord
            </button>
            <h1 className="font-serif text-3xl text-navy-900">Profil du véhicule</h1>
          </div>

          {/* Car selector */}
          {cars.length > 1 && (
            <div className="sm:w-64">
              <label className="block text-xs font-medium text-gray-500 mb-1">Véhicule</label>
              <select
                value={selectedCar.id}
                onChange={(e) => handleCarChange(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-900/30"
              >
                {cars.map((car) => (
                  <option key={car.id} value={car.id}>
                    {car.plate_number}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Status badge */}
        <div className="mb-6 flex items-center gap-3">
          <span className="font-serif text-2xl text-navy-900 font-bold">{selectedCar.plate_number}</span>
          <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${STATUS_COLORS[selectedCar.status] || "bg-gray-100 text-gray-600"}`}>
            {selectedCar.status === "active" ? "Actif" : "Inactif"}
          </span>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Vehicle information */}
          <Section title="Informations du véhicule">
            <Field label="Numéro d'immatriculation" value={selectedCar.plate_number} />
            <Field label="Numéro de châssis" value={selectedCar.chassis_number} />
            <Field label="Marque" value={selectedCar.vehicle_brand} />
            <Field label="Type de véhicule" value={selectedCar.vehicle_type} />
            <Field label="Énergie" value={POWER_LABELS[selectedCar.power_type] ?? selectedCar.power_type} />
            <Field label="Statut" value={selectedCar.status === "active" ? "Actif" : "Inactif"} />
            <Field label="Actif" value={selectedCar.is_active ? "Oui" : "Non"} />
          </Section>

          {/* Owner information */}
          <Section title="Informations du propriétaire">
            <Field label="Nom" value={selectedCar.owner_name} />
            <Field label="Prénom" value={selectedCar.owner_first_name} />
            <Field label="Téléphone" value={selectedCar.owner_phone} />
            <Field label="Email" value={selectedCar.owner_email} />
            <Field label="Numéro CNI" value={selectedCar.cni_number} />
            <Field label="Adresse" value={selectedCar.owner_address} />
          </Section>

          {/* Documents */}
          <Section title="Documents">
            <DocLink label="Photo de la plaque" url={selectedCar.plate_photo_url} />
            <DocLink label="Carte grise" url={selectedCar.cart_grise_url} />
            <DocLink label="Assurance" url={selectedCar.assurance_paper_url} />
            <DocLink label="Vignette" url={selectedCar.vignette_url} />
            <DocLink label="Contrôle technique" url={selectedCar.controle_technique_url} />
            <DocLink label="Permis de conduire" url={selectedCar.license_url} />
          </Section>

          {/* Metadata */}
          <Section title="Informations système">
            <Field label="Identifiant véhicule" value={selectedCar.id} />
            <Field label="QR Code" value={selectedCar.qr_code} />
            <Field label="Date d'enregistrement" value={formatDate(selectedCar.created_at)} />
            <Field label="Dernière mise à jour" value={formatDate(selectedCar.updated_at)} />
            <Field label="Durée de propriété" value={selectedCar.ownership_duration_days != null ? `${selectedCar.ownership_duration_days} jour(s)` : null} />
          </Section>
        </div>
      </div>
    </section>
  );
}
