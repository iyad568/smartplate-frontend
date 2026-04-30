import { Link } from "react-router-dom";
import { useLang } from "../i18n.jsx";

function ProductCard({
  title,
  priceLabel,
  price,
  smartsticksLabel,
  smartsticksPrice,
  buyLabel,
  showCondition = false,
  conditionLabel,
  imgSrc,
  imgAlt,
  buyLink,
}) {
  return (
    <article className="rounded-xl bg-[#0b1d3a] text-white overflow-hidden shadow-md">
      <div className="p-6 bg-gradient-to-br from-[#0e2249] to-[#0b1d3a]">
        <div className="aspect-[16/9] rounded-lg overflow-hidden bg-white/5">
          <img
            src={imgSrc}
            alt={imgAlt}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      </div>
      <div className="p-6">
        <h3 className="font-serif text-2xl">{title}</h3>
        <div className="mt-4 text-sm text-gray-200">
          {price ? (
            <>
              <span className="font-semibold">{priceLabel}:</span>{" "}
              <span>{price}</span>
            </>
          ) : (
            <span className="italic text-gray-300">{conditionLabel}</span>
          )}
        </div>
        {smartsticksPrice && (
          <div className="mt-1 text-sm text-gray-300">
            {smartsticksLabel}: {smartsticksPrice}
          </div>
        )}
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <Link to={buyLink || "/plaque-standard"} className="btn-primary">
            {buyLabel}
          </Link>
          {showCondition && (
            <button className="btn-danger">{conditionLabel}</button>
          )}
        </div>
      </div>
    </article>
  );
}

export default function Produits() {
  const { t } = useLang();
  const dz = t("dz");

  return (
    <section className="bg-white">
      <div className="container-x py-16">
        <h1 className="heading-serif">{t("products_title")}</h1>

        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <ProductCard
            title={t("product_standard")}
            priceLabel={t("price_label")}
            price={`2500 ${dz}`}
            smartsticksLabel={t("smartsticks_inline")}
            smartsticksPrice={`1000 ${dz}`}
            buyLabel={t("buy")}
            buyLink="/plaque-standard"
            imgSrc="/photo_2026-04-28_11-22-53.jpg"
            imgAlt="Plaque Standard"
          />
          <ProductCard
            title={t("product_silver")}
            priceLabel={t("price_label")}
            price={`6500 ${dz}`}
            smartsticksLabel={t("smartsticks_inline")}
            smartsticksPrice={`1000 ${dz}`}
            buyLabel={t("buy")}
            buyLink="/plaque-silver"
            imgSrc="/photo_2026-04-28_11-23-25.jpg"
            imgAlt="Plaque Silver"
          />
          <ProductCard
            title={t("product_gold")}
            buyLabel={t("buy")}
            buyLink="/plaque-gold"
            showCondition
            conditionLabel={t("conditions")}
            imgSrc="/photo_2026-04-28_11-23-21.jpg"
            imgAlt="Plaque Gold"
          />
        </div>

        <p className="mt-6 text-center text-sm text-gray-500">
          {t("auction")} — {t("product_gold")}
        </p>

        {/* Auction notice */}
        <div className="mt-12 max-w-3xl mx-auto rounded-xl overflow-hidden border border-gray-100 shadow-sm">
          <img
            src="/photo_2026-04-28_11-23-32.jpg"
            alt="Récapitulatif de l'enchère"
            className="w-full h-auto"
            loading="lazy"
          />
        </div>

        {/* Plates gallery */}
        <div className="mt-16">
          <h2 className="font-serif text-3xl text-navy-900 text-center">
            Plus de modèles
          </h2>
          <div className="mt-8 rounded-2xl overflow-hidden shadow-md">
            <img
              src="/photo_2026-04-28_11-23-54.jpg"
              alt="Modèles de plaques personnalisées"
              className="w-full h-auto object-cover"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
