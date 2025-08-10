export function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="glass glass-hover p-6 transition-all duration-200">
      <div className="flex items-baseline justify-between">
        <div className="text-sm text-[var(--color-muted)] font-medium">{label}</div>
        <div className="text-xs px-2 py-0.5 rounded-full bg-white/10">live</div>
      </div>
      <div className="text-3xl font-bold tracking-tight text-gradient mt-2">{value}</div>
    </div>
  );
}


