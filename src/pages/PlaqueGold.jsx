import { useEffect, useState } from "react";
import { useLang } from "../i18n.jsx";

const AUCTIONS = [
  {
    id: "BLID09DZ",
    label: "BLID09DZ",
    img: "/photo_2026-04-28_11-23-41.jpg",
    startPrice: 150000,
    deadline: Date.now() + (3 * 24 + 10) * 60 * 60 * 1000 + 5 * 60 * 1000,
    lastBidder: "ali***@gmail.com",
  },
  {
    id: "ORANDZ",
    label: "ORANDZ",
    img: "/photo_2026-04-28_11-23-59.jpg",
    startPrice: 160000,
    deadline: Date.now() + (2 * 24 + 6) * 60 * 60 * 1000 + 23 * 60 * 1000,
    lastBidder: "moh25***@gmail.com",
  },
  {
    id: "FENNEC",
    label: "FENNEC",
    img: "/photo_2026-04-28_11-23-36.jpg",
    startPrice: 250000,
    deadline: Date.now() + (1 * 24 + 9) * 60 * 60 * 1000 + 53 * 60 * 1000,
    lastBidder: "billy23***@gmail.com",
  },
];

function formatPrice(n) {
  return n.toLocaleString("fr-FR").replace(/ |\s/g, ".");
}

function useCountdown(target) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 60000);
    return () => clearInterval(id);
  }, []);
  const diff = Math.max(0, target - now);
  const days = Math.floor(diff / (24 * 3600 * 1000));
  const hours = Math.floor((diff % (24 * 3600 * 1000)) / (3600 * 1000));
  const minutes = Math.floor((diff % (3600 * 1000)) / 60000);
  return { days, hours, minutes };
}

function AuctionCard({ item }) {
  const { t } = useLang();
  const { days, hours, minutes } = useCountdown(item.deadline);
  const [offer, setOffer] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!offer) return;
    alert(`${t("pg_my_offer")} ${item.label}: ${offer} DZ`);
  };

  return (
    <article className="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden flex flex-col">
      <div className="bg-gradient-to-br from-[#bdaee0] via-[#a072c8] to-[#7e3db0] h-40 flex items-center justify-center p-4">
        <img
          src={item.img}
          alt={item.label}
          className="w-full h-full object-contain drop-shadow-md"
          loading="lazy"
        />
      </div>
      <div className="p-6 space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">{t("pg_starting")}</span>
          <span className="font-semibold text-navy-900">
            {formatPrice(item.startPrice)} DZ
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">{t("pg_time_left")}</span>
          <span className="font-semibold text-navy-900">
            {days}J {hours}H {minutes}M
          </span>
        </div>
        <div className="text-gray-500 text-xs">
          {t("pg_last_bidder")}:{" "}
          <span className="text-navy-900 font-medium">{item.lastBidder}</span>
        </div>

        <form onSubmit={submit} className="pt-3 flex gap-2 border-t border-gray-100">
          <input
            type="number"
            min={item.startPrice}
            value={offer}
            onChange={(e) => setOffer(e.target.value)}
            placeholder={t("pg_my_offer")}
            className="flex-1 rounded-md border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-900/30"
          />
          <button
            type="submit"
            className="rounded-md bg-navy-900 text-white px-4 py-2 text-sm font-medium hover:bg-navy-800 transition"
          >
            {t("pg_submit")}
          </button>
        </form>
      </div>
    </article>
  );
}

export default function PlaqueGold() {
  const { t } = useLang();
  const [search, setSearch] = useState("");

  return (
    <>
      <section className="relative bg-gradient-to-br from-[#caa15a] via-[#a07a2a] to-[#3b2406] text-white">
        <div className="container-x py-20 text-center">
          <h1 className="font-serif text-3xl md:text-5xl">{t("pg_title")}</h1>
          <p className="mt-2 text-amber-100">{t("pg_smartsticks_free")}</p>
        </div>
      </section>

      <section className="bg-gray-50">
        <div className="container-x py-14">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-serif text-2xl text-navy-900">{t("pg_top")}</h2>
            <a
              href="#"
              className="text-sm text-navy-900 hover:underline font-medium"
            >
              {t("pg_more")}
            </a>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {AUCTIONS.map((a) => (
              <AuctionCard key={a.id} item={a} />
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white">
        <div className="container-x py-12">
          <h2 className="font-serif text-2xl text-navy-900 mb-4">
            {t("pg_preview")}
          </h2>
          <div className="rounded-xl border border-gray-100 bg-gray-50 p-6 flex flex-col md:flex-row gap-6 items-center">
            <div className="flex-1 w-full">
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {t("pg_search")}
              </label>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value.toUpperCase())}
                placeholder="DZ-..."
                className="w-full rounded-md border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-navy-900/30"
              />
            </div>
            <div className="rounded-md bg-amber-400 border-2 border-amber-700 px-6 py-4 min-w-[220px] text-center">
              <span className="font-bold text-2xl tracking-widest text-amber-900">
                {search || "BLIDA"}
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
