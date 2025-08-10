"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import PageHeader from "@/components/marketing/PageHeader";

type Workshop = { title: string; description?: string };
type AgendaItem = { time?: string; title: string; description?: string };
type HackathonPlan = {
  target_audience?: string;
  location?: string;
  dates?: string;
  workshops?: Workshop[];
  agenda?: AgendaItem[];
};

type Hackathon = {
  _id: string;
  topic: string;
  description?: string;
  target_audience?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  status: string;
  plan?: HackathonPlan;
};

export default function HackathonsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);

  // draft form
  const [topic, setTopic] = useState("");
  const [description, setDescription] = useState("");
  const [audience, setAudience] = useState("");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [invitingId, setInvitingId] = useState<string | null>(null);
  const [sendingId, setSendingId] = useState<string | null>(null);

  const refresh = async () => {
    try {
      setLoading(true);
      const res = await api.get<Hackathon[]>("/hackathons/", { params: { limit: 50 } });
      setHackathons(res.data ?? []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const submitDraft = async () => {
    try {
      setSubmitting(true);
      const res = await api.post<Hackathon>("/hackathons/generate-plan", {
        topic,
        description,
        target_audience: audience,
        location,
        start_date: startDate,
        end_date: endDate,
      });
      setTopic("");
      setDescription("");
      setAudience("");
      setLocation("");
      setStartDate("");
      setEndDate("");
      setHackathons((prev) => [res.data, ...prev]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate plan");
    } finally {
      setSubmitting(false);
    }
  };

  const invite = async (id: string) => {
    try {
      setInvitingId(id);
      await api.post<number>(`/hackathons/${id}/invite`, null, { params: { limit: 20 } });
      await refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create invites");
    } finally {
      setInvitingId(null);
    }
  };

  const sendEmails = async (id: string) => {
    try {
      setSendingId(id);
      await api.post<number>(`/hackathons/${id}/send-emails`, null, { params: { limit: 20, dry_run: true } });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to send emails");
    } finally {
      setSendingId(null);
    }
  };

  return (
    <main className="maxw">
      <PageHeader title="Hackathons" subtitle="Create a hackathon plan with AI, then invite and email participants." />

      {error ? (
        <div className="glass px-6 py-4 border border-red-500/20 mb-6">
          <span className="text-red-400">Error:</span> {error}
        </div>
      ) : null}

      <Card>
        <CardHeader title="Create Hackathon" subtitle="AI will generate a structured plan based on your inputs." />
        <CardBody>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input placeholder="Topic" className="glass-input" value={topic} onChange={(e) => setTopic(e.target.value)} />
            <input placeholder="Target audience" className="glass-input" value={audience} onChange={(e) => setAudience(e.target.value)} />
            <input placeholder="Location" className="glass-input" value={location} onChange={(e) => setLocation(e.target.value)} />
            <div className="flex gap-3">
              <input placeholder="Start date" className="glass-input flex-1" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              <input placeholder="End date" className="glass-input flex-1" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <textarea placeholder="Description" className="glass-input sm:col-span-2 min-h-24" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="mt-4 flex justify-end">
            <Button onClick={submitDraft} disabled={!topic || submitting}>
              {submitting ? "Generating…" : "Generate Plan"}
            </Button>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="All Hackathons" subtitle="Latest entries" />
        <CardBody>
          <ul className="space-y-3">
            {(loading ? [] : hackathons).map((h) => (
              <li key={h._id} className="glass p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="font-semibold text-lg mb-1">{h.topic}</div>
                    <div className="text-sm text-[var(--color-muted)] mb-2">
                      {h.location ? `${h.location} · ` : ""}
                      {h.start_date || ""}{h.end_date ? ` – ${h.end_date}` : ""}
                    </div>
                    {h.plan ? (
                      <div className="text-sm">
                        <div className="font-medium mb-1">Workshops</div>
                        <ul className="list-disc ml-5 mb-2">
                          {(h.plan.workshops || []).slice(0, 3).map((w, idx) => (
                            <li key={idx}>{w.title}</li>
                          ))}
                        </ul>
                        <div className="font-medium mb-1">Agenda</div>
                        <ul className="list-disc ml-5">
                          {(h.plan.agenda || []).slice(0, 3).map((a, idx) => (
                            <li key={idx}>{a.time ? `${a.time} ` : ""}{a.title}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                  </div>
                  <div className="flex flex-col gap-2 min-w-[180px]">
                    <Button onClick={() => invite(h._id)} disabled={invitingId === h._id}>
                      {invitingId === h._id ? "Inviting…" : "Create Invites"}
                    </Button>
                    <Button onClick={() => sendEmails(h._id)} variant="glass" disabled={sendingId === h._id}>
                      {sendingId === h._id ? "Sending…" : "Send Emails (dry)"}
                    </Button>
                  </div>
                </div>
              </li>
            ))}
            {!loading && hackathons.length === 0 && (
              <div className="text-sm text-[var(--color-muted)]">No hackathons yet.</div>
            )}
          </ul>
        </CardBody>
      </Card>
    </main>
  );
}


