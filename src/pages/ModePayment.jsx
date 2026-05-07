import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function ModePayment() {
  const location = useLocation();
  const navigate = useNavigate();
  const { product, price } = location.state || {};
  const [selected, setSelected] = useState(null);
  const [confirmed, setConfirmed] = useState(false);

  const methods = [
    {
      id: "dahabia",
      label: "Dahabia",
      desc: "Carte Dahabia — Algérie Poste",
      img: "/dahabia.jpg",
    },
    {
      id: "cib",
      label: "CIB",
      desc: "Carte Interbancaire (CIB)",
      img: "/cib.jpg",
    },
  ];

  if (confirmed) {
    return (
      <section className="min-h-[70vh] bg-[#0b1d3a] grid place-items-center px-4">
        <div className="text-center text-white space-y-4">
          <div className="w-20 h-20 mx-auto rounded-full bg-green-500/20 grid place-items-center">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="#22c55e" strokeWidth="2" />
              <path d="M7 12l4 4 6-7" stroke="#22c55e" strokeWidth="2.5"
                strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <h2 className="font-serif text-3xl">Commande confirmée !</h2>
          <p className="text-gray-300 text-sm max-w-xs mx-auto">
            Votre commande a été enregistrée. Notre équipe vous contactera
            sous 24h pour finaliser le paiement par <strong>{methods.find(m => m.id === selected)?.label}</strong>.
          </p>
          <button
            onClick={() => navigate("/")}
            className="mt-4 rounded-md bg-white text-[#0b1d3a] font-semibold px-6 py-2.5 hover:bg-gray-100 transition"
          >
            Retour à l'accueil
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="min-h-[70vh] bg-[#0b1d3a] py-16 px-4 text-white">
      <div className="max-w-xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="font-serif text-3xl md:text-4xl">Mode de paiement</h1>
          {product && (
            <p className="mt-2 text-gray-300 text-sm">
              {product} — <span className="text-white font-semibold">{price}</span>
            </p>
          )}
          <p className="mt-3 text-gray-400 text-sm">
            Choisissez votre mode de paiement ci-dessous
          </p>
        </div>

        {/* Payment method cards */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          {methods.map((m) => (
            <button
              key={m.id}
              onClick={() => setSelected(m.id)}
              className={`rounded-xl border-2 p-4 flex flex-col items-center gap-3 transition
                ${selected === m.id
                  ? "border-blue-400 bg-blue-500/10"
                  : "border-white/10 bg-[#0e2249] hover:border-white/30"
                }`}
            >
              <img
                src={m.img}
                alt={m.label}
                className="w-full h-28 object-contain rounded-lg"
              />
              <div className="text-center">
                <p className="font-semibold text-base">{m.label}</p>
                <p className="text-xs text-gray-400 mt-0.5">{m.desc}</p>
              </div>
              {selected === m.id && (
                <span className="text-xs text-blue-400 font-medium">✓ Sélectionné</span>
              )}
            </button>
          ))}
        </div>

        {/* Info box */}
        <div className="rounded-xl bg-white/5 border border-white/10 p-4 mb-6 text-sm text-gray-300">
          <p className="font-semibold text-white mb-2">Comment ça marche ?</p>
          <ol className="space-y-1.5 list-decimal list-inside">
            <li>Sélectionnez votre mode de paiement</li>
            <li>Confirmez votre commande</li>
            <li>Notre équipe vous contacte sous 24h avec les détails de paiement</li>
            <li>Après confirmation du paiement, votre commande est traitée</li>
          </ol>
        </div>

        {/* Confirm button */}
        <button
          disabled={!selected}
          onClick={() => setConfirmed(true)}
          className="w-full rounded-xl bg-white text-[#0b1d3a] font-bold py-3 text-lg
            hover:bg-gray-100 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {selected
            ? `Confirmer avec ${methods.find(m => m.id === selected)?.label}`
            : "Sélectionnez un mode de paiement"}
        </button>

        <button
          onClick={() => navigate(-1)}
          className="w-full mt-3 text-gray-400 hover:text-white text-sm transition"
        >
          ← Retour
        </button>

      </div>
    </section>
  );
}
