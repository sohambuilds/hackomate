"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import PageHeader from "@/components/marketing/PageHeader";

type Profile = { _id: string; name?: string; location?: string; status?: string };

export default function CommunityPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [profiles, setProfiles] = useState<Profile[]>([]);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const res = await api.get("/profiles/", { params: { limit: 50 } });
      setProfiles(res.data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
    const id = setInterval(fetchProfiles, 5000); // simple polling for demo
    return () => clearInterval(id);
  }, []);

  return (
    <main className="maxw">
      <PageHeader title="Community" subtitle="Live feed and member directory for your hackathon." />
      {error ? (
        <div className="glass px-6 py-4 border border-red-500/20 mb-6">
          <span className="text-red-400">Error:</span> {error}
        </div>
      ) : null}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Live Feed" subtitle="Recent joins and activity (polling)" />
          <CardBody>
            {loading ? (
              <div className="space-y-2">
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </div>
            ) : (
              <ul className="space-y-2">
                {profiles.slice(0, 10).map((p) => (
                  <li key={p._id} className="text-sm flex justify-between">
                    <span>{p.name || "New member"}</span>
                    <span className="text-[var(--color-muted)]">{p.location || ""}</span>
                  </li>
                ))}
                {profiles.length === 0 && (
                  <div className="text-sm text-[var(--color-muted)]">No activity yet.</div>
                )}
              </ul>
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Members" subtitle="Directory (first 20)" />
          <CardBody>
            {loading ? (
              <div className="space-y-2">
                <Skeleton />
                <Skeleton />
                <Skeleton />
              </div>
            ) : (
              <ul className="space-y-2">
                {profiles.slice(0, 20).map((p) => (
                  <li key={p._id} className="text-sm">
                    <span className="font-medium">{p.name || "Unnamed"}</span>
                    <span className="text-[var(--color-muted)]">{p.location ? ` • ${p.location}` : ""}</span>
                  </li>
                ))}
                {profiles.length === 0 && (
                  <div className="text-sm text-[var(--color-muted)]">No members.</div>
                )}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
    </main>
  );
}


