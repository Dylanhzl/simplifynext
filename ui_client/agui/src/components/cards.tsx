import type { ReactNode } from "react";

/**
 * Artifact components.
 *
 * One component per render tool the CDR agent can call. These are registered
 * two ways: in the artifact drawer (driven by the AG-UI event stream) and on
 * CopilotKitProvider's `renderToolCalls`, so a tool call the agent makes from
 * chat renders the same card inline. This is the AG-UI contract - the agent
 * emits a tool call, the UI mounts a component, not a wall of chat text.
 *
 * Adding a tool: write a component, add one line to CARDS. Anything not in
 * CARDS still renders through UnknownCard rather than disappearing.
 */

type Args = Record<string, any>;

function Shell({
  ico, title, tool, cls, children,
}: { ico: string; title: string; tool: string; cls?: string; children: ReactNode }) {
  return (
    <article className={`card ${cls ?? ""}`}>
      <header>
        <span className="ico">{ico}</span>
        <h3>{title}</h3>
        <span className="tool">{tool}</span>
      </header>
      <div className="body">{children}</div>
    </article>
  );
}

const Bullets = ({ items }: { items?: string[] }) =>
  !items?.length ? null : <ul>{items.map((i, n) => <li key={n}>{i}</li>)}</ul>;

const Section = ({ h, children }: { h: string; children: ReactNode }) => (
  <section><h4>{h}</h4>{children}</section>
);

/* ------------------------------------------------------------------ */

export function ResearchBrief({ a }: { a: Args }) {
  return (
    <Shell ico="🔍" title="Research brief" tool="render_research_brief">
      <Section h="Angle"><p>{a.angle}</p></Section>
      <Section h="Audience read"><Bullets items={a.audience_read} /></Section>
      <Section h="Competitor read"><Bullets items={a.competitor_read} /></Section>
      {a.sources?.length ? (
        <Section h="Sources">
          <ul>{a.sources.map((s: Args, n: number) => (
            <li key={n}><b>{s.label}</b> — {s.note}</li>
          ))}</ul>
        </Section>
      ) : null}
      {a.recommended_slots?.length ? (
        <Section h="Recommended slots">
          <div className="tags">{a.recommended_slots.map((s: string) => <span key={s}>{s}</span>)}</div>
        </Section>
      ) : null}
    </Shell>
  );
}

export function ContentPackage({ a }: { a: Args }) {
  const v2 = (a.version ?? 1) > 1;
  return (
    <Shell ico="🎬" title={`Content package · v${a.version ?? 1}`} tool="render_content_package" cls={v2 ? "pass" : ""}>
      <Section h={v2 ? "Hook · rewritten" : "Hook"}>
        <div className="hookbox">{a.hook}</div>
      </Section>
      {v2 && a.changes?.length ? <Section h="What changed"><Bullets items={a.changes} /></Section> : null}
      <Section h={`Script · ${a.duration_s ?? 60}s`}>
        <ul className="beats">
          {(a.script ?? []).map((b: Args, n: number) => (
            <li key={n}><span className="t">{b.t}</span><span>{b.beat}</span></li>
          ))}
        </ul>
      </Section>
      <Section h="Shot list"><Bullets items={a.shot_list} /></Section>
      <Section h="Caption">
        <p>{a.caption}</p>
        <div className="tags">{(a.hashtags ?? []).map((h: string) => <span key={h}>{h}</span>)}</div>
      </Section>
      <div className="kv">
        <span>{a.platform ?? "tiktok"}</span><span>{a.package_id}</span><span>{a.status}</span>
      </div>
    </Shell>
  );
}

export function QaVerdict({ a }: { a: Args }) {
  const failed = a.verdict === "fail";
  return (
    <Shell
      ico={failed ? "⛔" : "✅"}
      title={`Critique · iteration ${a.iteration}/${a.max_iterations ?? 3}`}
      tool="render_qa_verdict"
      cls={failed ? "fail" : "pass"}
    >
      <section style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <span className={`verdict-pill ${failed ? "fail" : "pass"}`}>{a.verdict}</span>
        <span className={`score ${a.score >= 0.7 ? "hi" : a.score >= 0.5 ? "mid" : "lo"}`}>
          {typeof a.score === "number" ? a.score.toFixed(2) : ""}
        </span>
      </section>
      {a.critics?.length ? (
        <Section h="Critics">
          <div className="kv">{a.critics.map((c: Args, n: number) => (
            <span key={n}>{c.agent} · {c.verdict}</span>
          ))}</div>
        </Section>
      ) : null}
      {a.issues?.length ? <Section h="Issues"><Bullets items={a.issues} /></Section> : null}
      {a.must_fix?.length ? <Section h="Must fix"><Bullets items={a.must_fix} /></Section> : null}
      {a.resolved?.length ? <Section h="Resolved"><Bullets items={a.resolved} /></Section> : null}
    </Shell>
  );
}

export function OutreachEmail({ a }: { a: Args }) {
  const rc: Args = a.rate_card ?? {};
  return (
    <Shell
      ico="✉️"
      title={a.status === "sent" ? "Email · sent" : "Email · draft"}
      tool="render_outreach_email"
      cls={a.status === "sent" ? "pass" : ""}
    >
      <div className="email">
        <div className="hdr">To: {a.to_name} &lt;{a.to}&gt;</div>
        <div className="hdr">From: {a.from_name ?? "Maya Tan"}</div>
        <div className="subj">{a.subject}</div>
        <pre>{a.body}</pre>
      </div>
      {Object.keys(rc).length ? (
        <div className="kv">
          {Object.entries(rc).map(([k, v]) => (
            <span key={k}>{k.replace(/_/g, " ")}: {String(v)}</span>
          ))}
        </div>
      ) : null}
      {a.adapted_from?.length ? <Section h="Adapted from memory"><Bullets items={a.adapted_from} /></Section> : null}
    </Shell>
  );
}

export function DmScript({ a }: { a: Args }) {
  return (
    <Shell ico="💬" title={`DM · ${a.status ?? "draft"}`} tool="render_dm_script">
      <div className="email">
        <div className="hdr">{a.channel} → {a.to}</div>
        <pre>{a.message}</pre>
      </div>
      <div className="kv"><span>send {a.scheduled_for ?? "now"}</span><span>{a.status}</span></div>
    </Shell>
  );
}

export function CallScript({ a }: { a: Args }) {
  return (
    <Shell ico="📞" title="Call script" tool="render_call_script">
      <Section h="Opening"><div className="hookbox">{a.opening}</div></Section>
      <Section h="Key points"><Bullets items={a.key_points} /></Section>
      {a.objections?.length ? (
        <Section h="Objections">
          {a.objections.map((o: Args, n: number) => (
            <div className="obj" key={n}><b>“{o.objection}”</b>{o.response}</div>
          ))}
        </Section>
      ) : null}
      <Section h="Close"><p>{a.close}</p></Section>
    </Shell>
  );
}

export function CalendarCard({ a }: { a: Args }) {
  return (
    <Shell ico="📅" title={`Calendar · week of ${a.week_of}`} tool="render_calendar_week">
      <div className="calendar">
        {(a.slots ?? []).map((d: Args) => (
          <div className="day" key={d.day}>
            <h3>{d.day}</h3>
            {(d.items ?? []).map((i: Args, n: number) => (
              <div className={`slot ${i.kind}`} key={n}>
                <span className="t">{i.time}</span>{i.title}
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="kv"><span>{a.timezone ?? "Asia/Singapore"}</span></div>
    </Shell>
  );
}

export function EngagementReply({ a }: { a: Args }) {
  return (
    <Shell
      ico="📥"
      title={`Reply · ${a.classification}`}
      tool="render_engagement_reply"
      cls={a.classification === "interested" ? "pass" : ""}
    >
      <div className="email">
        <div className="hdr">{a.from} · {a.channel} · {a.received}</div>
        <pre>{a.body}</pre>
      </div>
      <div className="kv">
        <span>{a.classification}</span>
        <span>confidence {a.confidence}</span>
        <span>→ {a.suggested_status}</span>
      </div>
      {a.extracted_asks?.length ? <Section h="Extracted asks"><Bullets items={a.extracted_asks} /></Section> : null}
    </Shell>
  );
}

export function Analytics({ a }: { a: Args }) {
  const posts: Args[] = a.posts ?? [];
  const max = Math.max(1, ...posts.map((p) => p.vs_median ?? 0));
  return (
    <Shell ico="📊" title={`Performance · ${a.window}`} tool="render_analytics">
      <div className="bars">
        {posts.map((p, n) => (
          <div className={`bar-row ${p.verdict}`} key={n}>
            <div className="lbl"><b>{p.title}</b><span>{p.vs_median}× median</span></div>
            <div className="bar"><i style={{ width: `${Math.round(((p.vs_median ?? 0) / max) * 100)}%` }} /></div>
          </div>
        ))}
      </div>
      <Section h="Signal"><p>{a.signal}</p></Section>
    </Shell>
  );
}

export function PlanAdaptation({ a }: { a: Args }) {
  return (
    <Shell ico="🧠" title={`Plan adapted · week of ${a.week_of}`} tool="render_plan_adaptation" cls="pass">
      <Section h="Driver"><p>{a.driver}</p></Section>
      <Section h="Changes">
        <ul className="deltas">
          {(a.changes ?? []).map((c: Args, n: number) => (
            <li key={n}>
              <span className="item">{c.item}<span className="why">{c.why}</span></span>
              <span className="arrow"><s>{String(c.before)}</s> → <b>{String(c.after)}</b></span>
            </li>
          ))}
        </ul>
      </Section>
      <Section h="Net effect"><p>{a.net_effect}</p></Section>
    </Shell>
  );
}

export function UnknownCard({ name, a }: { name: string; a: Args }) {
  return (
    <Shell ico="◫" title={name} tool="unregistered tool">
      <pre style={{ font: "11px/1.5 var(--mono)", whiteSpace: "pre-wrap", color: "var(--ink-2)", margin: 0 }}>
        {JSON.stringify(a, null, 2)}
      </pre>
    </Shell>
  );
}

/* ------------------------------------------------------------------ */

export const CARDS: Record<string, (p: { a: Args }) => JSX.Element> = {
  render_research_brief: ResearchBrief,
  render_content_package: ContentPackage,
  render_qa_verdict: QaVerdict,
  render_outreach_email: OutreachEmail,
  render_dm_script: DmScript,
  render_call_script: CallScript,
  render_calendar_week: CalendarCard,
  render_engagement_reply: EngagementReply,
  render_analytics: Analytics,
  render_plan_adaptation: PlanAdaptation,
};

export function renderCard(name: string, args: Args) {
  const C = CARDS[name];
  return C ? <C a={args} /> : <UnknownCard name={name} a={args} />;
}
