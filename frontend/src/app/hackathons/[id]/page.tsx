"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import PageHeader from "@/components/marketing/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

type Workshop = { title: string; description?: string };
type AgendaItem = { time?: string; title: string; description?: string };
type ProblemStatement = { 
  title: string; 
  description: string; 
  difficulty?: string; 
  skills_required?: string[];
};
type HackathonPlan = {
  target_audience?: string;
  location?: string;
  dates?: string;
  workshops?: Workshop[];
  agenda?: AgendaItem[];
  problem_statements?: ProblemStatement[];
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

export default function HackathonDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hackathon, setHackathon] = useState<Hackathon | null>(null);
  const [inviting, setInviting] = useState(false);
  const [sending, setSending] = useState(false);
  const [generatingProblems, setGeneratingProblems] = useState(false);

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        setLoading(true);
        const res = await api.get<Hackathon>(`/hackathons/${id}`);
        setHackathon(res.data);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load hackathon");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const createInvites = async () => {
    if (!id) return;
    try {
      setInviting(true);
      await api.post<number>(`/hackathons/${id}/invite`, null, { params: { limit: 20 } });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create invites");
    } finally {
      setInviting(false);
    }
  };

  const sendEmails = async () => {
    if (!id) return;
    try {
      setSending(true);
      await api.post<number>(`/hackathons/${id}/send-emails`, null, { params: { limit: 20, dry_run: true } });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to send emails");
    } finally {
      setSending(false);
    }
  };

  const generateProblems = async () => {
    if (!id) return;
    try {
      setGeneratingProblems(true);
      const res = await api.post<Hackathon>(`/hackathons/${id}/generate-problems`);
      setHackathon(res.data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate problem statements");
    } finally {
      setGeneratingProblems(false);
    }
  };

  const title = hackathon?.topic || "Hackathon";
  const subtitle = hackathon
    ? `${hackathon.location ? hackathon.location + " · " : ""}${hackathon.start_date || ""}${hackathon.end_date ? ` – ${hackathon.end_date}` : ""}`
    : "";

  return (
    <main className="maxw relative">
      {/* Page-specific gradient orbs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute w-[800px] h-[400px] -top-40 left-1/4 bg-gradient-to-r from-blue-500/8 to-cyan-500/6 rounded-full blur-3xl opacity-40"></div>
        <div className="absolute w-[600px] h-[600px] top-1/2 -right-40 bg-gradient-to-l from-purple-500/6 to-pink-500/4 rounded-full blur-3xl opacity-30"></div>
      </div>

      <PageHeader title={title} subtitle={subtitle} />
      
      {error ? (
        <div className="glass px-6 py-4 border border-red-500/20 mb-6 bg-gradient-to-r from-red-950/20 to-red-900/10">
          <span className="text-red-400">Error:</span> {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 relative z-10">
        <div className="lg:col-span-3 space-y-6">
          {/* Overview Section */}
          <Card>
            <CardHeader title="Event Overview" subtitle="Essential details at a glance" />
            <CardBody>
              {loading || !hackathon ? (
                <div className="space-y-3">
                  <Skeleton />
                  <Skeleton />
                  <Skeleton />
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="relative overflow-hidden rounded-lg border border-blue-500/20 bg-gradient-to-br from-blue-950/20 via-blue-900/10 to-transparent hover:border-blue-500/30 transition-all duration-300 group">
                      <div className="glass-hover px-5 py-4">
                        <div className="text-xs text-blue-400 mb-2 font-medium tracking-wide uppercase">Audience</div>
                        <div className="text-sm font-medium text-blue-100">{hackathon.plan?.target_audience || hackathon.target_audience || "—"}</div>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                    <div className="relative overflow-hidden rounded-lg border border-emerald-500/20 bg-gradient-to-br from-emerald-950/20 via-emerald-900/10 to-transparent hover:border-emerald-500/30 transition-all duration-300 group">
                      <div className="glass-hover px-5 py-4">
                        <div className="text-xs text-emerald-400 mb-2 font-medium tracking-wide uppercase">Location</div>
                        <div className="text-sm font-medium text-emerald-100">{hackathon.plan?.location || hackathon.location || "—"}</div>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                    <div className="relative overflow-hidden rounded-lg border border-violet-500/20 bg-gradient-to-br from-violet-950/20 via-violet-900/10 to-transparent hover:border-violet-500/30 transition-all duration-300 group">
                      <div className="glass-hover px-5 py-4">
                        <div className="text-xs text-violet-400 mb-2 font-medium tracking-wide uppercase">Duration</div>
                        <div className="text-sm font-medium text-violet-100">{hackathon.plan?.dates || subtitle || "—"}</div>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  </div>

                  {hackathon.description ? (
                    <div className="relative overflow-hidden p-5 rounded-lg border border-slate-500/20 bg-gradient-to-br from-slate-800/20 via-slate-700/10 to-transparent">
                      <div className="text-sm text-slate-200 leading-relaxed relative z-10">{hackathon.description}</div>
                      <div className="absolute inset-0 bg-gradient-to-r from-slate-600/5 to-transparent"></div>
                    </div>
                  ) : null}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Workshops Section */}
          <Card>
            <CardHeader title="Workshops" subtitle="Learning sessions and skill-building activities" />
            <CardBody>
              {loading || !hackathon ? (
                <div className="space-y-2"><Skeleton /><Skeleton /></div>
              ) : (
                <div className="space-y-3">
                  {(hackathon.plan?.workshops || []).map((w, i) => (
                    <div key={i} className="relative overflow-hidden p-5 rounded-lg border border-amber-500/20 bg-gradient-to-br from-amber-950/15 via-amber-900/8 to-transparent hover:border-amber-500/30 transition-all duration-300 group">
                      <div className="relative z-10">
                        <div className="font-medium text-amber-200 mb-2 text-base">{w.title}</div>
                        {w.description && <div className="text-sm text-amber-100/80 leading-relaxed">{w.description}</div>}
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  ))}
                  {(hackathon.plan?.workshops || []).length === 0 && (
                    <div className="text-sm text-[var(--color-muted)] p-4 text-center rounded-lg border border-slate-600/20 bg-slate-800/10">No workshops listed yet.</div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Agenda Section */}
          <Card>
            <CardHeader title="Schedule" subtitle="Complete day-by-day agenda" />
            <CardBody>
              {loading || !hackathon ? (
                <div className="space-y-2"><Skeleton /><Skeleton /></div>
              ) : (
                <div className="space-y-3">
                  {(hackathon.plan?.agenda || []).map((a, i) => (
                    <div key={i} className="relative overflow-hidden flex items-start gap-4 p-4 rounded-lg border border-teal-500/20 bg-gradient-to-br from-teal-950/15 via-teal-900/8 to-transparent hover:border-teal-500/30 transition-all duration-300 group">
                      {a.time && (
                        <div className="text-sm font-mono text-teal-300 bg-gradient-to-r from-teal-900/30 to-teal-800/20 px-3 py-2 rounded-lg font-medium min-w-[90px] text-center border border-teal-500/20">
                          {a.time}
                        </div>
                      )}
                      <div className="flex-1 relative z-10">
                        <div className="font-medium text-teal-200 mb-1 text-base">{a.title}</div>
                        {a.description && <div className="text-sm text-teal-100/80 leading-relaxed">{a.description}</div>}
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  ))}
                  {(hackathon.plan?.agenda || []).length === 0 && (
                    <div className="text-sm text-[var(--color-muted)] p-4 text-center rounded-lg border border-slate-600/20 bg-slate-800/10">No agenda items yet.</div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Problem Statements Section */}
          <Card>
            <CardHeader title="Problem Statements" subtitle="Challenge problems for participants to solve" />
            <CardBody>
              {loading || !hackathon ? (
                <div className="space-y-2"><Skeleton /><Skeleton /></div>
              ) : (
                <div className="space-y-4">
                  {(hackathon.plan?.problem_statements || []).map((p, i) => (
                    <div key={i} className="relative overflow-hidden p-6 rounded-lg border border-rose-500/20 bg-gradient-to-br from-rose-950/15 via-rose-900/8 to-transparent hover:border-rose-500/30 transition-all duration-300 group">
                      <div className="relative z-10">
                        <div className="flex items-start justify-between gap-4 mb-4">
                          <h4 className="font-semibold text-rose-200 text-lg">{p.title}</h4>
                          {p.difficulty && (
                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                              p.difficulty === "easy" ? "bg-gradient-to-r from-green-900/30 to-green-800/20 text-green-300 border border-green-500/30" :
                              p.difficulty === "medium" ? "bg-gradient-to-r from-yellow-900/30 to-yellow-800/20 text-yellow-300 border border-yellow-500/30" :
                              "bg-gradient-to-r from-red-900/30 to-red-800/20 text-red-300 border border-red-500/30"
                            }`}>
                              {p.difficulty}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-rose-100/80 leading-relaxed mb-4">{p.description}</p>
                        {p.skills_required && p.skills_required.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {p.skills_required.map((skill, idx) => (
                              <span key={idx} className="px-3 py-1 text-xs bg-gradient-to-r from-rose-900/25 to-rose-800/15 text-rose-300/90 rounded-full border border-rose-500/25">
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-rose-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  ))}
                  {(hackathon.plan?.problem_statements || []).length === 0 && (
                    <div className="text-sm text-[var(--color-muted)] p-6 text-center rounded-lg border border-slate-600/20 bg-gradient-to-r from-slate-800/15 to-slate-700/10">
                      No problem statements generated yet. Use the &quot;Generate Problems&quot; button to create some!
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="Actions" />
            <CardBody>
              <div className="flex flex-col gap-4">
                <Button 
                  onClick={generateProblems} 
                  disabled={generatingProblems || loading} 
                  className="relative overflow-hidden bg-gradient-to-r from-purple-600/70 to-pink-600/70 hover:from-purple-500/80 hover:to-pink-500/80 border-purple-500/30 shadow-lg shadow-purple-500/20"
                >
                  <span className="relative z-10">{generatingProblems ? "Generating…" : "Generate Problems"}</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-400/10 to-pink-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                </Button>
                <Button 
                  onClick={createInvites} 
                  disabled={inviting || loading} 
                  className="relative overflow-hidden bg-gradient-to-r from-green-600/70 to-emerald-600/70 hover:from-green-500/80 hover:to-emerald-500/80 border-green-500/30 shadow-lg shadow-green-500/20"
                >
                  <span className="relative z-10">{inviting ? "Creating Invites…" : "Create Invites"}</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-green-400/10 to-emerald-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                </Button>
                <Button 
                  onClick={sendEmails} 
                  variant="glass" 
                  disabled={sending || loading} 
                  className="relative overflow-hidden border-blue-500/30 hover:border-blue-400/40 bg-gradient-to-r from-blue-950/20 to-blue-900/10"
                >
                  <span className="relative z-10">{sending ? "Sending…" : "Send Emails (dry)"}</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
                </Button>
              </div>
            </CardBody>
          </Card>
          
          <Card>
            <CardHeader title="Details" />
            <CardBody>
              {loading || !hackathon ? (
                <div className="space-y-2"><Skeleton /><Skeleton /><Skeleton /></div>
              ) : (
                <div className="space-y-3">
                  <div className="relative overflow-hidden p-4 rounded-lg border border-slate-500/20 bg-gradient-to-r from-slate-800/20 to-slate-700/10 group">
                    <div className="flex items-start justify-between gap-3">
                      <span className="text-xs text-slate-400 uppercase tracking-wide font-medium flex-shrink-0">Status</span>
                      <span className="text-sm font-medium px-3 py-1 rounded-full bg-gradient-to-r from-green-900/30 to-green-800/20 text-green-300 border border-green-500/30 text-right">{hackathon.status}</span>
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-r from-slate-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </div>
                  {hackathon.target_audience && (
                    <div className="relative overflow-hidden p-4 rounded-lg border border-slate-500/20 bg-gradient-to-r from-slate-800/20 to-slate-700/10 group">
                      <div className="flex items-start justify-between gap-3">
                        <span className="text-xs text-slate-400 uppercase tracking-wide font-medium flex-shrink-0 w-20">Audience</span>
                        <span className="text-sm text-slate-200 font-medium text-right flex-1">{hackathon.target_audience}</span>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-slate-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  )}
                  {hackathon.location && (
                    <div className="relative overflow-hidden p-4 rounded-lg border border-slate-500/20 bg-gradient-to-r from-slate-800/20 to-slate-700/10 group">
                      <div className="flex items-start justify-between gap-3">
                        <span className="text-xs text-slate-400 uppercase tracking-wide font-medium flex-shrink-0 w-20">Location</span>
                        <span className="text-sm text-slate-200 font-medium text-right flex-1">{hackathon.location}</span>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-slate-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  )}
                  {(hackathon.start_date || hackathon.end_date) && (
                    <div className="relative overflow-hidden p-4 rounded-lg border border-slate-500/20 bg-gradient-to-r from-slate-800/20 to-slate-700/10 group">
                      <div className="flex items-start justify-between gap-3">
                        <span className="text-xs text-slate-400 uppercase tracking-wide font-medium flex-shrink-0 w-20">Dates</span>
                        <span className="text-sm text-slate-200 font-medium text-right flex-1">{hackathon.start_date || ""}{hackathon.end_date ? ` – ${hackathon.end_date}` : ""}</span>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-slate-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </main>
  );
}


