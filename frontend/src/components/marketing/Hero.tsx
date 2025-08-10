"use client";
import Link from "next/link";
import { useRef } from "react";

export default function Hero() {
  const ref = useRef<HTMLDivElement>(null);

  const onMouseMove: React.MouseEventHandler<HTMLDivElement> = (e) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width - 0.5;
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    el.style.setProperty("--rx", `${py * -6}deg`);
    el.style.setProperty("--ry", `${px * 6}deg`);
  };

  const onMouseLeave: React.MouseEventHandler<HTMLDivElement> = () => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--rx", `0deg`);
    el.style.setProperty("--ry", `0deg`);
  };

  return (
    <section className="hero-wrap glass p-10 md:p-16 mt-8 animate-fadeIn" onMouseMove={onMouseMove} onMouseLeave={onMouseLeave}>
      <div className="grid-overlay" />
      <div className="aurora-orb orb-1 float-slow" />
      <div className="aurora-orb orb-2 float-med" />
      <div className="aurora-orb orb-3 float-fast" />

      <div ref={ref} className="relative parallax">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-semibold tracking-tight mb-5 shine-text">
            Autopilot for Hackathons
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-muted)] mb-8 leading-relaxed">
            Recruit, form teams, and launch challenges with AI agents — in minutes, not weeks.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard" className="glass glass-hover px-6 py-3 text-sm font-medium rounded-lg">
              Open Dashboard
            </Link>
            <a href="#features" className="px-6 py-3 text-sm font-medium rounded-lg hover:bg-white/5">
              See how it works
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}


