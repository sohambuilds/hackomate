"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/community", label: "Community" },
  { href: "/challenges", label: "Challenges" },
  { href: "/teams", label: "Teams" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="glass px-6 py-4 sticky top-6 z-50 maxw animate-fadeIn">
      <div className="flex items-center justify-between">
        <div className="text-xl font-semibold tracking-tight text-gradient">
          <span className="mr-2">⚡</span>Hackathon Twin
        </div>
        <ul className="flex gap-2 text-sm text-[var(--color-muted)]">
          {links.map((l) => {
            const active = pathname.startsWith(l.href);
            return (
              <li key={l.href}>
                <Link
                  href={l.href}
                  className={`px-4 py-2 rounded-full ring-focus transition-all duration-200 ${
                    active 
                      ? "text-[var(--color-foreground)] bg-white/10 shadow-lg" 
                      : "hover:text-[var(--color-foreground)] hover:bg-white/5"
                  }`}
                >
                  {l.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}


