type Feature = { title: string; desc: string; tag?: string };

export default function FeatureGrid({ features }: { features: Feature[] }) {
  return (
    <section id="features" className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
      {features.map((f) => (
        <div key={f.title} className="glass glass-hover p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold">{f.title}</h3>
            {f.tag ? <span className="px-2 py-0.5 rounded-full text-xs bg-white/10">{f.tag}</span> : null}
          </div>
          <p className="text-sm text-[var(--color-muted)] leading-relaxed">{f.desc}</p>
        </div>
      ))}
    </section>
  );
}


