import Hero from "@/components/marketing/Hero";
import FeatureGrid from "@/components/marketing/FeatureGrid";
// Removed mid‑page brand strip to avoid visual noise on hero
import CTA from "@/components/marketing/CTA";

export default function Home() {
  return (
    <main className="maxw">
      <Hero />
      <FeatureGrid
        features={[
          { title: "AI Recruitment", desc: "Agents search, dedupe and enrich developer profiles across the web.", tag: "agent" },
          { title: "Smart Teaming", desc: "Auto‑match people into balanced, skill‑complete teams.", tag: "matching" },
          { title: "Challenge Engine", desc: "Generate, curate, and publish hackathon challenges instantly.", tag: "gen" },
        ]}
      />
      <CTA />
    </main>
  );
}
