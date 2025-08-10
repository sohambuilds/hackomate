import Link from "next/link";

export default function CTA() {
  return (
    <section className="mt-10 glass glass-hover p-8 text-center">
      <h3 className="text-2xl font-semibold tracking-tight mb-2">Spin up your autonomous hackathon</h3>
      <p className="text-sm text-[var(--color-muted)] mb-5">Start with sample data, then connect real profiles and outreach in one click.</p>
      <Link href="/dashboard" className="glass glass-hover px-6 py-3 text-sm font-medium rounded-lg">
        Launch Dashboard
      </Link>
    </section>
  );
}


