import { useLang } from "../i18n.jsx";
import { useNavigate } from "react-router-dom";
import { userStore } from "../admin/store.js";

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
};

export default function Bienvenue() {
  const { t } = useLang();
  const navigate = useNavigate();
  const user = userStore.getCurrentUser();

  const handleLogout = () => {
    userStore.logout();
    navigate("/se-connecter");
  };

  // Add operator-specific tiles based on role
  const operatorTiles = [];
  if (user.role === "sos") {
    operatorTiles.push({
      key: "admin_tab_sos",
      icon: Icons.shield,
      onClick: () => navigate("/operator/sos")
    });
  } else if (user.role === "depannage") {
    operatorTiles.push({
      key: "admin_tab_dep",
      icon: Icons.shield,
      onClick: () => navigate("/operator/depannage")
    });
  }

  const tiles = [
    { key: "dash_qr", icon: Icons.qr },
    { key: "dash_pwd", icon: Icons.key },
    { key: "dash_view_plate", icon: Icons.plate },
    { key: "dash_print_lic", icon: Icons.print },
    { key: "dash_insurance", icon: Icons.shield },
    { key: "dash_sell", icon: Icons.sell },
    ...operatorTiles,
  ];

  return (
    <section className="bg-gray-50 min-h-[80vh]">
      <div className="container-x py-10">
        {/* Top welcome bar */}
        <div className="rounded-2xl bg-gradient-to-r from-navy-900 to-navy-800 text-white p-6 md:p-8 shadow-md flex flex-col md:flex-row items-start md:items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-white/15 grid place-items-center text-2xl font-bold">
            {user.fullname?.charAt(0) || "U"}
          </div>
          <div className="flex-1">
            <h1 className="font-serif text-3xl md:text-4xl">
              {t("dash_welcome")}, <span className="font-semibold">{user.fullname || "Utilisateur"}</span>
            </h1>
            <p className="text-sm text-blue-100 mt-1">
              SMART PLATE dz • {user.role === "sos" ? "Opérateur SOS" : user.role === "depannage" ? "Opérateur Dépannage" : "Utilisateur"}
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
                <img
                  src="/photo_2026-04-28_11-22-53.jpg"
                  alt="Ma plaque immatriculation"
                  className="w-full h-auto rounded-lg object-cover"
                  loading="lazy"
                />
                <div className="mt-4 grid grid-cols-2 gap-3 text-center text-xs">
                  <div className="rounded-md bg-gray-50 p-3">
                    <div className="text-navy-900 font-bold">2549 VF 23</div>
                    <div className="text-gray-500 mt-1">Immatriculation</div>
                  </div>
                  <div className="rounded-md bg-gray-50 p-3">
                    <div className="text-navy-900 font-bold">Active</div>
                    <div className="text-gray-500 mt-1">Statut</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gray-50 p-5">
                <h2 className="font-serif text-lg text-navy-900">
                  {t("dash_qr")}
                </h2>
              </div>
              <div className="p-5">
                <div className="aspect-square w-40 mx-auto bg-white border border-gray-200 rounded-lg grid place-items-center">
                  <div className="w-32 h-32 grid grid-cols-7 gap-0.5">
                    {Array.from({ length: 49 }).map((_, i) => (
                      <div
                        key={i}
                        className={
                          [0, 1, 2, 3, 5, 7, 8, 11, 12, 14, 16, 18, 19, 22, 24, 27, 30, 32, 34, 36, 38, 41, 43, 44, 46, 48].includes(i)
                            ? "bg-navy-900"
                            : "bg-white"
                        }
                      />
                    ))}
                  </div>
                </div>
                <p className="text-xs text-gray-500 text-center mt-3">
                  Scan pour identifier votre véhicule
                </p>
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

            {/* Insurance card teaser */}
            <div className="mt-6 rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden grid sm:grid-cols-2">
              <img
                src="/photo_2026-04-28_11-22-58.jpg"
                alt="Carte Algérie Poste"
                className="w-full h-full object-cover"
                loading="lazy"
              />
              <div className="p-6 flex flex-col justify-center">
                <h3 className="font-serif text-xl text-navy-900">
                  {t("dash_insurance")}
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {t("about_phone")}
                </p>
                <button className="mt-4 inline-flex items-center justify-center self-start rounded-md bg-navy-900 text-white px-4 py-2 text-sm font-medium hover:bg-navy-800 transition">
                  Voir détails
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
