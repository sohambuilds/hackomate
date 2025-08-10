export function Skeleton({ className = "h-6 w-full" }: { className?: string }) {
  return <div className={`relative overflow-hidden rounded-lg bg-white/5 ${className}`}>
    <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent" />
  </div>;
}


