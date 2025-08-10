"use client";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import PageHeader from "@/components/marketing/PageHeader";

type Team = {
  _id: string;
  name: string;
  members?: string[];
  skills_needed?: string[];
  challenge_id?: string;
};

export default function TeamsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [query, setQuery] = useState("");
  const [filterChallenge, setFilterChallenge] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await api.get<Team[]>("/teams", { params: { limit: 50 } });
        setTeams(res.data ?? []);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filtered = useMemo(() => {
    return teams.filter((t) => {
      const okQ = query ? t.name?.toLowerCase().includes(query.toLowerCase()) : true;
      const okC = filterChallenge ? t.challenge_id === filterChallenge : true;
      return okQ && okC;
    });
  }, [teams, query, filterChallenge]);

  return (
    <main className="maxw">
      <PageHeader title="Teams" subtitle="Discover teams, see skills, and track challenge assignments." />
      {error ? (
        <div className="glass px-6 py-4 border border-red-500/20 mb-6">
          <span className="text-red-400">Error:</span> {error}
        </div>
      ) : null}
      <Card>
        <CardHeader title="All Teams" subtitle="Latest entries" />
        <CardBody>
          <div className="flex gap-3 mb-6">
            <input
              placeholder="Search teams..."
              className="glass-input flex-1 text-sm"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <input
              placeholder="Filter by challenge ID"
              className="glass-input text-sm min-w-[160px]"
              value={filterChallenge}
              onChange={(e) => setFilterChallenge(e.target.value)}
            />
            <Button onClick={() => { setQuery(""); setFilterChallenge(""); }} variant="ghost">Reset</Button>
          </div>
          <ul className="space-y-3">
            {(loading ? [] : filtered).map((t: Team) => (
              <li key={t._id} className="glass glass-hover p-6 cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-lg mb-1">{t.name}</div>
                    <div className="text-sm text-[var(--color-muted)]">
                      <span className="glass px-2 py-1 rounded text-xs mr-2">
                        {t.members?.length || 0} members
                      </span>
                      Skills: {(t.skills_needed || []).join(", ")}
                    </div>
                  </div>
                  <div className="text-sm text-[var(--color-muted)] ml-4">
                    {t.challenge_id ? (
                      <span className="glass px-3 py-1 text-xs font-medium">
                        Challenge: {t.challenge_id.slice(0, 8)}...
                      </span>
                    ) : (
                      <span className="text-orange-400">Unassigned</span>
                    )}
                  </div>
                </div>
              </li>
            ))}
            {(!loading && filtered.length === 0) && (
              <div className="text-sm text-[var(--color-muted)]">No teams yet.</div>
            )}
          </ul>
        </CardBody>
      </Card>
    </main>
  );
}


