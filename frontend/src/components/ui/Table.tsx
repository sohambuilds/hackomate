import { ReactNode } from "react";

export function Table({ children }: { children: ReactNode }) {
  return <div className="glass overflow-hidden">
    <table className="w-full text-sm">
      {children}
    </table>
  </div>;
}

export function THead({ children }: { children: ReactNode }) {
  return <thead className="bg-white/5 border-b border-white/10">{children}</thead>;
}

export function TH({ children }: { children: ReactNode }) {
  return <th className="text-left px-4 py-2 font-medium">{children}</th>;
}

export function TBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-white/10">{children}</tbody>;
}

export function TR({ children }: { children: ReactNode }) {
  return <tr className="hover:bg-white/5 transition-colors">{children}</tr>;
}

export function TD({ children }: { children: ReactNode }) {
  return <td className="px-4 py-2">{children}</td>;
}


