import { ButtonHTMLAttributes, ReactNode } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "glass" | "ghost";
};

export function Button({ children, className = "", variant = "glass", ...rest }: Props) {
  const base =
    variant === "glass"
      ? "glass glass-hover px-5 py-3 text-sm font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
      : "px-5 py-3 text-sm font-medium text-[var(--color-foreground)]/80 hover:text-[var(--color-foreground)] hover:bg-white/5 rounded-lg";
  return (
    <button className={`${base} ring-focus ${className}`} {...rest}>
      {children}
    </button>
  );
}


