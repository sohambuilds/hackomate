import { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`glass glass-hover ${className}`}>{children}</div>;
}

export function CardHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="border-b border-white/10 px-6 py-5">
      <h3 className="text-xl font-semibold tracking-tight">{title}</h3>
      {subtitle ? (
        <p className="text-sm text-[var(--color-muted)] mt-1">{subtitle}</p>
      ) : null}
    </div>
  );
}

export function CardBody({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`px-6 py-5 ${className}`}>{children}</div>;
}


