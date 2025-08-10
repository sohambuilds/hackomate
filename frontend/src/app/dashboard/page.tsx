"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Stat } from "@/components/ui/Stat";
import { Skeleton } from "@/components/ui/Skeleton";
import PageHeader from "@/components/marketing/PageHeader";
import { Button } from "@/components/ui/Button";

type Profile = { _id: string };
type Team = { _id: string };
type Challenge = { _id: string };

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [recentTeams, setRecentTeams] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const [p, t, c] = await Promise.all([
          api.get("/profiles/", { params: { limit: 50 } }),
          api.get("/teams", { params: { limit: 50 } }),
          api.get("/challenges/", { params: { limit: 50 } }),
        ]);
        setProfiles(p.data || []);
        setTeams(t.data || []);
        setChallenges(c.data || []);
        setRecentTeams((t.data || []).slice(0, 8));
      } catch (e: any) {
        setError(e?.message || "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <main className="maxw">
      <PageHeader title="Dashboard" subtitle="Your live activity: profiles, teams and challenges at a glance." />
      <div className="flex items-center justify-end mb-6">
        <div className="flex gap-3">
          <Button variant="glass">Generate Challenges</Button>
          <Button variant="glass">Find Developers</Button>
          <Button variant="glass">Send Outreach</Button>
        </div>
      </div>
      
      {error ? (
        <div className="glass px-6 py-4 border border-red-500/20 mb-6">
          <span className="text-red-400">Error:</span> {error}
        </div>
      ) : null}
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <Stat label="Total Profiles" value={loading ? "…" : profiles.length} />
        <Stat label="Active Teams" value={loading ? "…" : teams.length} />
        <Stat label="Live Challenges" value={loading ? "…" : challenges.length} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card>
          <CardHeader title="Recent Profiles" subtitle="Latest 8 profiles" />
          <CardBody>
            {loading ? (
              <div className="space-y-2">
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </div>
            ) : (
              <ul className="space-y-2">
                {profiles.slice(0, 8).map((p: any) => (
                  <li key={p._id} className="flex justify-between text-sm">
                    <span>{p.name || "Unnamed"}</span>
                    <span className="text-[var(--color-muted)]">{p.location || ""}</span>
                  </li>
                ))}
                {profiles.length === 0 && (
                  <div className="text-sm text-[var(--color-muted)]">No profiles yet.</div>
                )}
              </ul>
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Recent Challenges" subtitle="Latest 8 challenges" />
          <CardBody>
            {loading ? (
              <div className="space-y-2">
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </div>
            ) : (
              <ul className="space-y-2">
                {challenges.slice(0, 8).map((c: any) => (
                  <li key={c._id} className="flex justify-between text-sm">
                    <span>{c.title}</span>
                    <span className="text-[var(--color-muted)]">{c.difficulty}</span>
                  </li>
                ))}
                {challenges.length === 0 && (
                  <div className="text-sm text-[var(--color-muted)]">No challenges yet.</div>
                )}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 mt-6">
        <Card>
          <CardHeader title="Recent Teams" subtitle="Latest 8 teams" />
          <CardBody>
            {loading ? (
              <div className="space-y-2">
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </div>
            ) : (
              <ul className="space-y-2">
                {recentTeams.map((t: any) => (
                  <li key={t._id} className="flex justify-between text-sm">
                    <span className="font-medium">{t.name}</span>
                    <span className="text-[var(--color-muted)]">{t.members?.length || 0} members</span>
                  </li>
                ))}
                {recentTeams.length === 0 && (
                  <div className="text-sm text-[var(--color-muted)]">No teams yet.</div>
                )}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
    </main>
  );
}


