export default function Logos() {
  const logos = [
    { name: "Next.js", src: "/next.svg" },
    { name: "Vercel", src: "/vercel.svg" },
    { name: "Window", src: "/window.svg" },
    { name: "Globe", src: "/globe.svg" },
  ];
  return (
    <div className="mt-10 glass px-6 py-4">
      <div className="flex flex-wrap items-center justify-center gap-8 opacity-70">
        {logos.map((l) => (
          <img key={l.name} src={l.src} alt={l.name} className="h-6" />
        ))}
      </div>
    </div>
  );
}


