import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { apiService } from "../services/api.js";

export default function PlaqueStandard() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    first: "",
    phone: "",
    email: "",
    cni: "",
    address: "",
    chassis: "",
    type: "",
    brand: "",
    plate: "",
    power: "essence",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedCarId, setSelectedCarId] = useState(null);
  const [cartGriseFile, setCartGriseFile] = useState(null);
  const [cartGriseUploading, setCartGriseUploading] = useState(false);
  const [cars, setCars] = useState([]);
  const [loadingCars, setLoadingCars] = useState(false);

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  // Load user's cars
  const loadCars = async () => {
    setLoadingCars(true);
    try {
      const userCars = await apiService.getUserCars();
      setCars(userCars.cars || []);
    } catch (err) {
      console.error("Error loading cars:", err);
      setError("Erreur lors du chargement des véhicules");
    } finally {
      setLoadingCars(false);
    }
  };

  // Load cars on component mount
  useEffect(() => {
    loadCars();
  }, []);

  // Handle car selection
  const handleCarSelect = (car) => {
    setForm({
      name: car.owner_name || "",
      first: car.owner_first_name || "",
      phone: car.owner_phone || "",
      email: car.owner_email || "",
      cni: car.cni_number || "",
      address: car.owner_address || "",
      chassis: car.chassis_number || "",
      type: car.vehicle_type || "",
      brand: car.vehicle_brand || "",
      plate: car.plate_number || "",
      power: car.power_type || "essence",
    });
    setSelectedCarId(car.id);
    setError("");
  };

  const handleCartGriseUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setCartGriseUploading(true);
    try {
      const uploadResult = await apiService.uploadFile(file, 'cart_grise');
      setCartGriseFile(uploadResult.url);
      setError("");
    } catch (err) {
      setError("Erreur lors du téléchargement de la carte grise: " + err.message);
    } finally {
      setCartGriseUploading(false);
    }
  };

  const getCurrentPlateType = () => {
    const pathname = window.location.pathname;
    if (pathname.includes("plaque-silver")) return "silver";
    if (pathname.includes("plaque-gold")) return "gold";
    return "standard";
  };

  const handlePay = (e) => {
    e.preventDefault();
    const type = getCurrentPlateType();
    const priceMap = { standard: "2500 DZ", silver: "6500 DZ", gold: null };
    const nameMap = { standard: "Plaque Standard", silver: "Plaque Silver", gold: "Plaque Gold" };
    navigate("/mode-de-paiement", {
      state: {
        product: nameMap[type],
        price: priceMap[type],
      },
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    if (!form.name || !form.first || !form.phone || !form.email || !form.cni ||
        !form.address || !form.chassis || !form.type || !form.brand || !form.plate) {
      setError("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const orderData = {
        name: form.name,
        first: form.first,
        phone: form.phone,
        email: form.email,
        cni: form.cni,
        address: form.address,
        chassis: form.chassis,
        type: form.type,
        brand: form.brand,
        plate: form.plate,
        power: form.power,
        order_type: "plate_order",
        plate_type: getCurrentPlateType(),
        total_price: 5000.00,
        currency: "DZD",
        cart_grise_url: cartGriseFile, // Add cart grise URL
      };

      const order = await apiService.createOrder(orderData);
      
      // Show success message
      alert(`Commande créée avec succès! Numéro de commande: ${order.id}`);
      
      // Optionally redirect to order confirmation page
      // navigate(`/order-confirmation/${order.id}`);
      
    } catch (err) {
      console.error('Error creating order:', err);
      console.error('Error details:', err.response);
      
      // Handle 422 validation errors specifically
      if (err.message && err.message.includes('422')) {
        setError("Erreur de validation: Vérifiez tous les champs du formulaire");
      } else {
        setError(err.message || "Erreur lors de la création de la commande");
      }
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30 bg-white";

  return (
    <section className="bg-gradient-to-br from-gray-50 via-purple-100/40 to-gray-100">
      <div className="container-x py-16 grid lg:grid-cols-5 gap-10 items-start">
        {/* Form on the left (3 cols) */}
        <form
          onSubmit={handleSubmit}
          className="lg:col-span-3 bg-white rounded-2xl border border-gray-100 shadow-md p-6 md:p-8 space-y-5"
        >
          <h1 className="font-serif text-2xl md:text-3xl text-navy-900 mb-2">
            {t("ps_personal")}
          </h1>
          
          {/* Error Display */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700 text-sm">❌ {error}</p>
            </div>
          )}
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_name")}
              </label>
              <input
                name="name"
                required
                value={form.name}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_first")}
              </label>
              <input
                name="first"
                required
                value={form.first}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_phone")}
              </label>
              <input
                name="phone"
                type="tel"
                value={form.phone}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_email")}
              </label>
              <input
                name="email"
                type="email"
                required
                value={form.email}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_cni")}
              </label>
              <input
                name="cni"
                required
                value={form.cni}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_address")}
              </label>
              <input
                name="address"
                required
                value={form.address}
                onChange={onChange}
                className={inputClass}
              />
            </div>
          </div>

          <h2 className="font-serif text-2xl text-navy-900 pt-4 border-t border-gray-200">
            {t("ps_vehicle")}
          </h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_chassis")}
              </label>
              <input
                name="chassis"
                required
                value={form.chassis}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_type")}
              </label>
              <input
                name="type"
                required
                value={form.type}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_brand")}
              </label>
              <input
                name="brand"
                required
                value={form.brand}
                onChange={onChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("ps_plate_number")}
              </label>
              <input
                name="plate"
                required
                value={form.plate}
                onChange={onChange}
                className={inputClass}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">
              {t("ps_power")}
            </label>
            <div className="flex flex-wrap gap-4 text-sm">
              {["essence", "diesel", "gpl", "hybride"].map((p) => (
                <label key={p} className="inline-flex items-center gap-2">
                  <input
                    type="radio"
                    name="power"
                    value={p}
                    checked={form.power === p}
                    onChange={onChange}
                  />
                  {t(`ps_${p}`)}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {t("ps_attach_card")}
            </label>
            
            {/* Cart Grise Upload */}
            <div className="mb-4">
              <label className="block text-xs font-medium text-gray-600 mb-2">
                Carte Grise (Gray Card)
              </label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleCartGriseUpload}
                disabled={cartGriseUploading}
                className="w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30 bg-white text-sm"
              />
              {cartGriseUploading && (
                <p className="mt-2 text-sm text-blue-600">Téléchargement en cours...</p>
              )}
              {cartGriseFile && (
                <div className="mt-2 text-sm text-green-600">
                  ✅ Carte grise téléchargée avec succès
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-200">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">❌ {error}</p>
              </div>
            )}
            <div className="font-semibold text-navy-900">{t("ps_price")}</div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="rounded-md bg-gray-700 text-white px-5 py-2 text-sm font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Création..." : t("ps_register")}
              </button>
              <button
                type="button"
                onClick={handlePay}
                className="rounded-md bg-navy-900 text-white px-5 py-2 text-sm font-medium hover:bg-navy-800 transition"
              >
                {t("ps_pay")}
              </button>
            </div>
          </div>
        </form>

        {/* Plate preview on the right (2 cols) */}
        <aside className="lg:col-span-2 lg:sticky lg:top-24 space-y-4">
          <div className="rounded-2xl bg-white border border-gray-100 shadow-md overflow-hidden">
            <img
              src="/photo_2026-04-28_11-22-53.jpg"
              alt="Plaque d'immatriculation Standard"
              className="w-full h-auto object-cover"
              loading="lazy"
            />
            <div className="p-5 text-center">
              <h3 className="font-serif text-xl text-navy-900">
                {t("product_standard")}
              </h3>
              <p className="mt-1 text-sm text-gray-600">{t("ps_price")}</p>
            </div>
          </div>
          <div className="rounded-xl bg-navy-900/5 border border-navy-900/10 p-4 text-sm text-gray-700 text-center">
            {t("smartsticks_inline")} — 1000 {t("dz")}
          </div>
        </aside>
      </div>
    </section>
  );
}
