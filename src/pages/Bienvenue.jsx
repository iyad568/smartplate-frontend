import { useLang } from "../i18n.jsx";
import { useNavigate } from "react-router-dom";
import { userStore } from "../admin/store.js";
import { useState, useEffect } from "react";
import { apiService } from "../services/api.js";
import { QRCodeSVG } from "qrcode.react";

function Tile({ icon, label, onClick }) {
  return (
    <button
      onClick={onClick}
      className="group rounded-xl bg-white border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-navy-900/30 transition flex items-center gap-4 text-start w-full"
    >
      <span className="w-12 h-12 rounded-lg bg-navy-900/10 text-navy-900 grid place-items-center group-hover:bg-navy-900 group-hover:text-white transition shrink-0">
        {icon}
      </span>
      <span className="font-medium text-gray-800">{label}</span>
    </button>
  );
}

const Icons = {
  qr: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <rect x="3" y="3" width="7" height="7" stroke="currentColor" strokeWidth="2" />
      <rect x="14" y="3" width="7" height="7" stroke="currentColor" strokeWidth="2" />
      <rect x="3" y="14" width="7" height="7" stroke="currentColor" strokeWidth="2" />
      <rect x="14" y="14" width="3" height="3" fill="currentColor" />
      <rect x="18" y="18" width="3" height="3" fill="currentColor" />
    </svg>
  ),
  key: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <circle cx="8" cy="14" r="4" stroke="currentColor" strokeWidth="2" />
      <path d="M11 14h10v3M18 14v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  plate: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <rect x="3" y="7" width="18" height="10" rx="1" stroke="currentColor" strokeWidth="2" />
      <path d="M7 11h10M7 14h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  print: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <rect x="6" y="3" width="12" height="6" stroke="currentColor" strokeWidth="2" />
      <rect x="3" y="9" width="18" height="9" rx="1" stroke="currentColor" strokeWidth="2" />
      <rect x="7" y="14" width="10" height="6" stroke="currentColor" strokeWidth="2" />
    </svg>
  ),
  shield: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6l8-3z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    </svg>
  ),
  sell: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M21 12l-9 9-9-9 9-9 9 9z" stroke="currentColor" strokeWidth="2" />
      <circle cx="9" cy="9" r="1.5" fill="currentColor" />
    </svg>
  ),
  logout: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  profile: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
      <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
};

export default function Bienvenue() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cars, setCars] = useState([]);
  const [selectedCar, setSelectedCar] = useState(null);
  const [showPlateModal, setShowPlateModal] = useState(false);
  const [newPlateNumber, setNewPlateNumber] = useState("");
  const [creatingCar, setCreatingCar] = useState(false);
  const [plateError, setPlateError] = useState("");
  const [platePhotoUploading, setPlatePhotoUploading] = useState(false);
  const [platePhotoError, setPlatePhotoError] = useState("");
  const [avatarUploading, setAvatarUploading] = useState(false);

  // Load user cars and profile on component mount
  useEffect(() => {
    loadUserCars();
    apiService.getUserProfile().then(setUser).catch(() => {});
  }, []);

  const loadUserCars = async () => {
    try {
      const response = await apiService.getUserCars();
      const carList = response.cars || [];
      setCars(carList);

      if (carList.length > 0) {
        const savedId = localStorage.getItem('selected_car_id');
        const restored = savedId && carList.find(c => c.id === savedId);
        setSelectedCar(restored || carList[0]);
      }
    } catch (err) {
      console.error('Error loading cars:', err);
    }
  };

  const handleCreateCar = async (e) => {
    e.preventDefault();
    
    if (!newPlateNumber.trim()) {
      setPlateError("Veuillez entrer un numéro de plaque");
      return;
    }

    // Force check authentication state
    console.log('=== Before Car Creation ===');
    console.log('localStorage access_token:', localStorage.getItem('access_token'));
    console.log('apiService.isAuthenticated():', apiService.isAuthenticated());
    console.log('apiService.token:', apiService.token);
    
    // Check authentication before creating car
    if (!apiService.isAuthenticated()) {
      setPlateError("Vous devez être connecté pour créer un véhicule");
      return;
    }

    setCreatingCar(true);
    setPlateError("");

    try {
      console.log('Creating car with plate:', newPlateNumber.trim().toUpperCase());
      console.log('User authenticated:', apiService.isAuthenticated());
      console.log('Token exists:', !!apiService.token);
      
      const response = await apiService.createCar(newPlateNumber.trim().toUpperCase());
      const newCar = response.car;
      
      setCars([...cars, newCar]);
      setSelectedCar(newCar);
      localStorage.setItem('selected_car_id', newCar.id);
      setShowPlateModal(false);
      setNewPlateNumber("");
      
      console.log('Car created successfully:', newCar);
    } catch (err) {
      console.error('Error creating car:', err);
      console.error('Error details:', err.response?.data || err.message);
      
      if (err.message.includes('401') || err.message.includes('Unauthorized')) {
        setPlateError("Erreur d'authentification. Veuillez vous reconnecter.");
      } else {
        setPlateError(err.message || "Erreur lors de la création du véhicule");
      }
    } finally {
      setCreatingCar(false);
    }
  };

  // Test function to manually check authentication
  const testAuthentication = () => {
    console.log('=== Manual Auth Test ===');
    console.log('localStorage access_token:', localStorage.getItem('access_token'));
    console.log('localStorage refresh_token:', localStorage.getItem('refresh_token'));
    console.log('apiService.isAuthenticated():', apiService.isAuthenticated());
    console.log('apiService.token:', apiService.token);
    console.log('======================');
  };

  const handlePlatePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedCar) return;

    setPlatePhotoUploading(true);
    setPlatePhotoError("");
    try {
      await apiService.uploadPlatePhoto(selectedCar.id, file);
      // Reload cars so selectedCar gets the new plate_photo_url
      await loadUserCars();
    } catch (err) {
      setPlatePhotoError("Échec du téléchargement: " + err.message);
    } finally {
      setPlatePhotoUploading(false);
      e.target.value = "";
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setAvatarUploading(true);
    try {
      const { url } = await apiService.uploadFile(file, "profile");
      await apiService.updateProfilePicture(url);
      setUser((prev) => ({ ...prev, profile_picture: url }));
    } catch (err) {
      console.error("Avatar upload failed:", err);
    } finally {
      setAvatarUploading(false);
      e.target.value = "";
    }
  };

  const handleLogout = () => {
    userStore.logout();
    navigate("/se-connecter");
  };

  // Add operator-specific tiles based on role
  const operatorTiles = [];
  if (user && user.role === "sos") {
    operatorTiles.push({
      key: "admin_tab_sos",
      icon: Icons.shield,
      onClick: () => navigate("/operator/sos")
    });
  } else if (user && user.role === "depannage") {
    operatorTiles.push({
      key: "admin_tab_dep",
      icon: Icons.shield,
      onClick: () => navigate("/operator/depannage")
    });
  }

  const tiles = [
    {
      key: "dash_pwd",
      icon: Icons.key,
      onClick: () => navigate("/dashboard/change-password"),
    },
    {
      key: "dash_view_plate",
      icon: Icons.plate,
      onClick: () => setShowPlateModal(true),
    },
    { key: "dash_print_lic", icon: Icons.print, onClick: () => navigate("/dashboard/licence") },
    { key: "dash_insurance", icon: Icons.shield },
    { key: "dash_sell", icon: Icons.sell },
    {
      key: "dash_profile",
      icon: Icons.profile,
      onClick: () => navigate("/dashboard/profil"),
    },
    ...operatorTiles,
  ];

  return (
    <section className="bg-gray-50 min-h-[80vh]">
      <div className="container-x py-10">
        {/* Top welcome bar */}
        <div className="rounded-2xl bg-gradient-to-r from-navy-900 to-navy-800 text-white p-6 md:p-8 shadow-md flex flex-col md:flex-row items-start md:items-center gap-6">
          <label className="relative w-16 h-16 rounded-full cursor-pointer shrink-0 group">
            {user?.profile_picture ? (
              <img
                src={user.profile_picture}
                alt="Photo de profil"
                className="w-16 h-16 rounded-full object-cover"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-white/15 grid place-items-center text-2xl font-bold">
                {avatarUploading ? (
                  <svg className="animate-spin" width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                    <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" className="opacity-75" fill="currentColor" />
                  </svg>
                ) : (
                  user?.full_name?.charAt(0)?.toUpperCase() || "U"
                )}
              </div>
            )}
            {/* Hover overlay */}
            {!avatarUploading && (
              <div className="absolute inset-0 rounded-full bg-black/40 opacity-0 group-hover:opacity-100 transition grid place-items-center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              className="sr-only"
              disabled={avatarUploading}
              onChange={handleAvatarUpload}
            />
          </label>
          <div className="flex-1">
            <h1 className="font-serif text-3xl md:text-4xl">
              {t("dash_welcome")}, <span className="font-semibold">{user?.full_name || "Utilisateur"}</span>
            </h1>
            <p className="text-sm text-blue-100 mt-1">
              SMART PLATE dz • {user?.role === "sos" ? "Opérateur SOS" : user?.role === "depanage" ? "Opérateur Dépannage" : "Utilisateur"}
            </p>
          </div>
          <button 
            onClick={handleLogout}
            className="self-start md:self-auto inline-flex items-center gap-2 rounded-md border border-white/30 px-4 py-2 text-sm hover:bg-white/10 transition"
          >
            {Icons.logout}
            <span>Déconnexion</span>
          </button>
        </div>

        {/* Main grid: profile (left) + tiles (right) */}
        <div className="mt-8 grid lg:grid-cols-3 gap-6">
          {/* Profile / plate panel */}
          <aside className="lg:col-span-1 space-y-6">
            <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gray-50 p-5">
                <h2 className="font-serif text-lg text-navy-900">
                  {t("dash_view_plate")}
                </h2>
              </div>
              <div className="p-5">
                {selectedCar ? (
                  <div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Votre véhicule
                      </label>
                      <select
                        value={selectedCar.id}
                        onChange={(e) => {
                          const car = cars.find(c => c.id === e.target.value);
                          setSelectedCar(car);
                          localStorage.setItem('selected_car_id', car.id);
                        }}
                        className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
                      >
                        {cars.map((car) => (
                          <option key={car.id} value={car.id}>
                            {car.plate_number}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    {/* Plate photo */}
                    <div className="rounded-lg overflow-hidden border border-gray-200 bg-gray-50">
                      {selectedCar.plate_photo_url ? (
                        <img
                          src={selectedCar.plate_photo_url}
                          alt="Photo de la plaque"
                          className="w-full h-40 object-cover"
                        />
                      ) : (
                        <div className="h-40 flex flex-col items-center justify-center gap-2 text-gray-400">
                          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                            <rect x="3" y="7" width="18" height="10" rx="1" stroke="currentColor" strokeWidth="2" />
                            <path d="M7 11h10M7 14h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                          </svg>
                          <span className="text-xs">Aucune photo de plaque</span>
                        </div>
                      )}
                    </div>

                    {/* Upload button */}
                    <label className={`mt-3 flex items-center justify-center gap-2 w-full rounded-md border px-3 py-2 text-sm font-medium cursor-pointer transition
                      ${platePhotoUploading
                        ? "border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed"
                        : "border-navy-900/30 text-navy-900 hover:bg-navy-900/5"}`}
                    >
                      {platePhotoUploading ? (
                        <>
                          <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                            <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" className="opacity-75" fill="currentColor" />
                          </svg>
                          Téléchargement...
                        </>
                      ) : (
                        <>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                          {selectedCar.plate_photo_url ? "Changer la photo" : "Uploader la photo"}
                        </>
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        className="sr-only"
                        disabled={platePhotoUploading}
                        onChange={handlePlatePhotoUpload}
                      />
                    </label>

                    {platePhotoError && (
                      <p className="mt-2 text-xs text-red-600">{platePhotoError}</p>
                    )}

                    <button
                      onClick={() => setShowPlateModal(true)}
                      className="mt-3 w-full text-sm text-navy-600 hover:text-navy-700 font-medium"
                    >
                      + Ajouter un autre véhicule
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 grid place-items-center">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-gray-400">
                        <rect x="3" y="7" width="18" height="10" rx="1" stroke="currentColor" strokeWidth="2" />
                        <path d="M7 11h10M7 14h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                    </div>
                    <h3 className="text-gray-900 font-medium mb-2">
                      Aucun véhicule enregistré
                    </h3>
                    <p className="text-gray-500 text-sm mb-4">
                      Ajoutez votre véhicule pour commencer
                    </p>
                    <button
                      onClick={() => setShowPlateModal(true)}
                      className="inline-flex items-center gap-2 rounded-md bg-navy-900 text-white px-4 py-2 text-sm hover:bg-navy-800 transition"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                      Ajouter un véhicule
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gray-50 p-5">
                <h2 className="font-serif text-lg text-navy-900">
                  {t("dash_qr")}
                </h2>
              </div>
              <div className="p-5 flex flex-col items-center gap-3">
                {selectedCar?.qr_code ? (
                  <>
                    <div className="p-3 bg-white rounded-xl border border-gray-200 shadow-sm">
                      <QRCodeSVG
                        value={`${window.location.origin}/vehicle/${selectedCar.qr_code}`}
                        size={140}
                        bgColor="#ffffff"
                        fgColor="#0f2357"
                        level="M"
                        includeMargin={false}
                      />
                    </div>
                    <p className="text-xs text-gray-500 text-center leading-relaxed">
                      Scan pour identifier votre véhicule
                      <br />
                      <span className="text-gray-400">{selectedCar.plate_number}</span>
                    </p>
                    <a
                      href={`/vehicle/${selectedCar.qr_code}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-navy-900 hover:underline font-medium"
                    >
                      Voir la page publique →
                    </a>
                  </>
                ) : (
                  <div className="w-36 h-36 rounded-xl bg-gray-100 grid place-items-center text-gray-400 text-xs text-center p-3">
                    Sélectionnez un véhicule pour générer le QR code
                  </div>
                )}
              </div>
            </div>
          </aside>

          {/* Action tiles */}
          <div className="lg:col-span-2">
            <h2 className="font-serif text-2xl text-navy-900 mb-4">
              Actions rapides
            </h2>
            <div className="grid sm:grid-cols-2 gap-4">
              {tiles.map((tl) => (
                <Tile 
                  key={tl.key} 
                  icon={tl.icon} 
                  label={t(tl.key)} 
                  onClick={tl.onClick}
                />
              ))}
            </div>

          </div>
        </div>
      </div>

      {/* Plate Modal */}
      {showPlateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedCar ? "Ajouter un véhicule" : "Créer un véhicule"}
              </h3>
              <button
                onClick={() => {
                  setShowPlateModal(false);
                  setNewPlateNumber("");
                  setPlateError("");
                }}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            
            <div className="p-6">
              {plateError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-700 text-sm">❌ {plateError}</p>
                </div>
              )}

              <form onSubmit={handleCreateCar} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Numéro de plaque
                  </label>
                  <input
                    type="text"
                    value={newPlateNumber}
                    onChange={(e) => setNewPlateNumber(e.target.value)}
                    placeholder="Ex: 1234 ABC 56"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
                    disabled={creatingCar}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Entrez le numéro de plaque d'immatriculation
                  </p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                  <p className="text-sm text-blue-800">
                    💡 Le véhicule sera créé avec ce numéro de plaque. Vous pourrez compléter les autres informations plus tard.
                  </p>
                </div>
                
                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={creatingCar || !newPlateNumber.trim()}
                    className="flex-1 rounded-md bg-navy-900 text-white px-4 py-2 text-sm hover:bg-navy-800 disabled:opacity-50 transition"
                  >
                    {creatingCar ? (
                      <>
                        <svg className="animate-spin inline mr-2" width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                          <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" className="opacity-75" fill="currentColor" />
                        </svg>
                        Création...
                      </>
                    ) : (
                      "Créer le véhicule"
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowPlateModal(false);
                      setNewPlateNumber("");
                      setPlateError("");
                    }}
                    disabled={creatingCar}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-700 transition"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}