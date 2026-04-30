import { Link } from "react-router-dom";
import { useLang } from "../i18n.jsx";

function ServiceCard({ to, imgSrc, imgAlt, label, contain = false }) {
  const Wrapper = to ? Link : "button";
  const props = to ? { to } : { type: "button" };
  return (
    <Wrapper
      {...props}
      className="group rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden hover:shadow-md hover:border-navy-900/30 transition text-start w-full block"
    >
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
      <div className="p-5">
        <span className="font-medium text-gray-800">{label}</span>
      </div>
    </Wrapper>
  );
}

export default function Services() {
  const { t } = useLang();

  const items = [
    {
      key: "service_assu",
      img: "/ass.jpg",
      alt: "Assurance",
      contain: false,
    },
    {
      key: "service_ct",
      img: "/cntrol.jpg",
      alt: "Contrôle technique",
      contain: false,
    },
    {
      key: "service_vig",
      img: "/vigne.jpg",
      alt: "Vignette",
      contain: true,
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

      <section className="bg-gray-50">
        <div className="container-x py-16">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((it) => (
              <ServiceCard
                key={it.key}
                to={it.to}
                imgSrc={it.img}
                imgAlt={it.alt}
                label={t(it.key)}
                contain={it.contain}
              />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
