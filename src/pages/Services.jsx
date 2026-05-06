import { Link } from "react-router-dom";
import { useLang } from "../i18n.jsx";
import { useState, useEffect } from "react";
import { apiService } from "../services/api.js";

function ServiceCard({ to, imgSrc, imgAlt, label, contain = false, showUpload = false, serviceType, selectedCar }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [documentUrl, setDocumentUrl] = useState(null);
  const [loadingDoc, setLoadingDoc] = useState(false);

  // Load document when car changes
  useEffect(() => {
    if (selectedCar && serviceType) {
      loadDocument();
    }
  }, [selectedCar, serviceType]);

  const loadDocument = async () => {
    if (!selectedCar) return;
    
    setLoadingDoc(true);
    try {
      const documents = await apiService.getCarDocuments(selectedCar.id);
      
      // Map service types to document URLs
      const documentMap = {
        'vignette': 'vignette_url',
        'controle_technique': 'controle_technique_url',
        'assurance': 'assurance_paper_url',
        'cart_grise': 'cart_grise_url',
      };
      
      const urlField = documentMap[serviceType];
      setDocumentUrl(documents[urlField] || null);
    } catch (err) {
      console.error('Error loading document:', err);
    } finally {
      setLoadingDoc(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
    setSuccess("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Veuillez sélectionner un fichier d'abord");
      return;
    }

    // Check if user is authenticated
    if (!apiService.isAuthenticated()) {
      setError("Vous devez être connecté pour télécharger des documents");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      // Check if user has a car selected
      if (!selectedCar) {
        setError("Veuillez d'abord ajouter un véhicule");
        return;
      }
      
      let response;
      if (serviceType === "vignette") {
        response = await apiService.uploadVignette(selectedCar.id, file);
      } else if (serviceType === "controle_technique") {
        response = await apiService.uploadControleTechnique(selectedCar.id, file);
      } else if (serviceType === "assurance") {
        response = await apiService.uploadAssurance(selectedCar.id, file);
      } else if (serviceType === "cart_grise") {
        response = await apiService.uploadCartGrise(selectedCar.id, file);
      } else {
        throw new Error("Type de service non supporté");
      }

      setSuccess(`${label} téléchargé avec succès!`);
      setFile(null);
      // Reload documents to show the newly uploaded one
      await loadDocument();
    } catch (error) {
      console.error('Upload error:', error);
      setError(error.message || 'Échec du téléchargement');
    } finally {
      setUploading(false);
    }
  };

  const Wrapper = to ? Link : "button";
  const props = to ? { to } : { type: "button" };
  
  return (
    <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md hover:border-navy-900/30 transition text-start w-full">
      {to ? (
        <Link to={to} className="block">
          <div className="aspect-[16/9] bg-gray-50 overflow-hidden grid place-items-center">
            <img
              src={imgSrc}
              alt={imgAlt}
              className={
                contain
                  ? "max-h-full max-w-full object-contain p-4 group-hover:scale-105 transition duration-300"
                  : "w-full h-full object-cover group-hover:scale-105 transition duration-300"
              }
              loading="lazy"
            />
          </div>
        </Link>
      ) : (
        <div className="aspect-[16/9] bg-gray-50 overflow-hidden grid place-items-center">
          <img
            src={imgSrc}
            alt={imgAlt}
            className={
              contain
                ? "max-h-full max-w-full object-contain p-4 group-hover:scale-105 transition duration-300"
                : "w-full h-full object-cover group-hover:scale-105 transition duration-300"
            }
            loading="lazy"
          />
        </div>
      )}
      
      <div className="p-5">
        <span className="font-medium text-gray-800 block mb-3">{label}</span>
        
        {showUpload && (
          <div className="space-y-3">
            <input
              type="file"
              onChange={handleFileChange}
              disabled={uploading || !apiService.isAuthenticated()}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
              accept=".pdf,.jpg,.jpeg,.png"
            />
            <button
              onClick={handleUpload}
              disabled={!file || uploading || !apiService.isAuthenticated()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-200"
            >
              {uploading ? (
                <>
                  <svg className="animate-spin inline mr-2" width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                    <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" className="opacity-75" fill="currentColor" />
                  </svg>
                  Téléchargement...
                </>
              ) : `Télécharger ${label}`}
            </button>
            {file && (
              <p className="text-sm text-gray-600 truncate">
                Sélectionné: {file.name}
              </p>
            )}
            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
                ❌ {error}
              </p>
            )}
            {success && (
              <p className="text-sm text-green-600 bg-green-50 border border-green-200 rounded-md p-2">
                ✅ {success}
              </p>
            )}
            
            {/* Document Viewer */}
            {documentUrl && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  Document téléchargé:
                </div>
                <div className="space-y-2">
                  {documentUrl.includes('.pdf') ? (
                    <a
                      href={documentUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M10 19v-5h4v5c0 1.1.9 2 2 2h3c1.1 0 2-.9 2-2v-7h1l-5-5-5 5h1v7c0 1.1.9 2 2 2z" stroke="currentColor" strokeWidth="2" fill="none"/>
                      </svg>
                      Voir le PDF
                    </a>
                  ) : (
                    <div className="relative">
                      <img
                        src={documentUrl}
                        alt={`${label} document`}
                        className="w-full h-32 object-cover rounded-md border border-gray-200"
                        onClick={() => window.open(documentUrl, '_blank')}
                        style={{ cursor: 'pointer' }}
                      />
                      <div className="absolute top-2 right-2 bg-white bg-opacity-90 rounded-full p-1">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M10 19v-5h4v5c0 1.1.9 2 2 2h3c1.1 0 2-.9 2-2v-7h1l-5-5-5 5h1v7c0 1.1.9 2 2 2z" stroke="currentColor" strokeWidth="2" fill="none"/>
                        </svg>
                      </div>
                    </div>
                  )}
                  <p className="text-xs text-gray-500">
                    Cliquez pour ouvrir dans un nouvel onglet
                  </p>
                </div>
              </div>
            )}
            
            {loadingDoc && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
                    <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" className="opacity-75" fill="currentColor" />
                  </svg>
                  Chargement du document...
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Services() {
  const { t } = useLang();
  const [isAuthenticated, setIsAuthenticated] = useState(apiService.isAuthenticated());
  const [selectedCar, setSelectedCar] = useState(null);
  const [cars, setCars] = useState([]);

  useEffect(() => {
    const checkAuth = () => {
      setIsAuthenticated(apiService.isAuthenticated());
    };

    checkAuth();
    const interval = setInterval(checkAuth, 1000);
    return () => clearInterval(interval);
  }, []);

  // Load user's selected car
  useEffect(() => {
    if (isAuthenticated) {
      loadUserCars();
    }
  }, [isAuthenticated]);

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

  const handleCarChange = (carId) => {
    const car = cars.find(c => c.id === carId);
    if (car) {
      setSelectedCar(car);
      localStorage.setItem('selected_car_id', car.id);
    }
  };

  const items = [
    {
      key: "service_assu",
      img: "/ass.jpg",
      alt: "Assurance",
      contain: false,
      showUpload: true,
      serviceType: "assurance",
    },
    {
      key: "service_ct",
      img: "/cntrol.jpg",
      alt: "Contrôle technique",
      contain: false,
      showUpload: true,
      serviceType: "controle_technique",
    },
    {
      key: "service_vig",
      img: "/vigne.jpg",
      alt: "Vignette",
      contain: true,
      showUpload: true,
      serviceType: "vignette",
    },
    {
      key: "service_sos",
      img: "/sos.jpg",
      alt: "SOS",
      contain: true,
      to: "/sos",
    },
    {
      key: "service_dep",
      img: "/photo_2026-04-28_11-24-12.jpg",
      alt: "Dépannage",
      contain: true,
      to: "/depannage",
    },
  ];

  return (
    <>
      <section className="bg-gradient-to-br from-[#bdaee0] via-[#a072c8] to-[#7e3db0] text-white">
        <div className="container-x py-20 text-center">
          <h1 className="font-serif text-4xl md:text-5xl">
            {t("services_title")}
          </h1>
          <p className="mt-3 text-white/90 max-w-2xl mx-auto">
            {t("home_subtagline")}
          </p>
        </div>
      </section>

      {!isAuthenticated && (
        <section className="bg-yellow-50 border-b border-yellow-200">
          <div className="container-x py-4">
            <div className="flex items-center justify-center gap-2 text-yellow-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span className="font-medium">
                Vous devez être connecté pour télécharger des documents. 
                <Link to="/se-connecter" className="ml-2 text-yellow-900 underline hover:no-underline">
                  Se connecter
                </Link>
              </span>
            </div>
          </div>
        </section>
      )}

      {isAuthenticated && !selectedCar && (
        <section className="bg-blue-50 border-b border-blue-200">
          <div className="container-x py-4">
            <div className="flex items-center justify-center gap-2 text-blue-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="7" width="18" height="10" rx="1" stroke="currentColor" strokeWidth="2" />
                <path d="M7 11h10M7 14h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span className="font-medium">
                Vous devez ajouter un véhicule pour télécharger des documents. 
                <Link to="/bienvenue" className="ml-2 text-blue-900 underline hover:no-underline">
                  Ajouter un véhicule
                </Link>
              </span>
            </div>
          </div>
        </section>
      )}

      <section className="bg-gray-50">
        <div className="container-x py-16">
          {selectedCar && (
            <div className="mb-8 bg-white rounded-lg border border-gray-200 p-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Véhicule sélectionné
              </label>
              {cars.length > 1 ? (
                <select
                  value={selectedCar.id}
                  onChange={(e) => handleCarChange(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
                >
                  {cars.map((car) => (
                    <option key={car.id} value={car.id}>
                      {car.plate_number} ({car.status || 'Active'})
                    </option>
                  ))}
                </select>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-navy-900">
                    {selectedCar.plate_number}
                  </span>
                  <span className="text-sm text-gray-500">
                    ({selectedCar.status || 'Active'})
                  </span>
                </div>
              )}
            </div>
          )}
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((it) => (
              <ServiceCard
                key={it.key}
                to={it.to}
                imgSrc={it.img}
                imgAlt={it.alt}
                label={t(it.key)}
                contain={it.contain}
                showUpload={it.showUpload}
                serviceType={it.serviceType}
                selectedCar={selectedCar}
              />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
