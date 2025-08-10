export default function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="relative glass elev-2 page-header hero prominent p-8 md:p-12 mb-4">
      <div className="net-overlay" />
      <div className="hero-orb hero-orb-1" />
      <div className="hero-orb hero-orb-2" />
      <div className="hero-orb hero-orb-3" />
      <h1 className="relative text-3xl md:text-4xl font-semibold tracking-tight mb-2 drop-shadow-[0_2px_6px_rgba(0,0,0,0.6)]">{title}</h1>
      {subtitle ? (
        <p className="relative text-sm md:text-base text-[var(--color-muted)] max-w-2xl">{subtitle}</p>
      ) : null}
    </div>
  );
}


