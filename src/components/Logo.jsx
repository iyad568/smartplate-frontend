export default function Logo({ className = "" }) {
  return (
    <div
      className={`inline-flex items-center justify-center bg-white border border-gray-200 rounded-md shadow-sm px-3 py-2 ${className}`}
      aria-label="Smart Plate DZ"
    >
      <img
        src="/photo_2026-04-28_11-23-12.jpg"
        alt="Smart Plate DZ"
        className="h-12 w-auto object-contain"
      />
    </div>
  );
}
