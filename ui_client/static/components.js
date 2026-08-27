/* CreatorLoop artifact components.
 *
 * One renderer per agent-facing render tool. When the CDR agent emits a
 * TOOL_CALL for `render_content_package`, the drawer mounts a real component -
 * this is the AG-UI "expose tools to agents for dynamic rendering" contract,
 * implemented without a framework so it also works with no keys and no build.
 *
 * The React/CopilotKit app in ui_client/agui mirrors this registry with
 * useCopilotAction render handlers against the same tool names and args.
 */
(function () {
  "use strict";

  const esc = (s) =>
    String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  function el(html) {
    const t = document.createElement("template");
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }

  const list = (arr, cls) =>
    !arr || !arr.length ? "" : `<ul class="${cls || ""}">${arr.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;

  function shell({ ico, title, tool, cls, body }) {
    return el(`
      <article class="card ${cls || ""}">
        <header>
          <span class="ico">${ico}</span>
          <h3>${esc(title)}</h3>
          <span class="tool">${esc(tool)}</span>
        </header>
        <div class="body">${body}</div>
      </article>`);
  }

  const TOOLS = {

    /* ---------------------------------------------------------------- */
    render_research_brief(a) {
      const sources = (a.sources || [])
        .map((s) => `<li><b>${esc(s.label)}</b> — ${esc(s.note)}</li>`)
        .join("");
      return shell({
        ico: "🔍", title: "Research brief", tool: "render_research_brief",
        body: `
          <section><h4>Angle</h4><p>${esc(a.angle)}</p></section>
          <section><h4>Audience read</h4>${list(a.audience_read)}</section>
          <section><h4>Competitor read</h4>${list(a.competitor_read)}</section>
          ${sources ? `<section><h4>Sources</h4><ul>${sources}</ul></section>` : ""}
          ${(a.recommended_slots || []).length
            ? `<section><h4>Recommended slots</h4><div class="tags">${a.recommended_slots
                .map((s) => `<span>${esc(s)}</span>`).join("")}</div></section>` : ""}`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_content_package(a) {
      const beats = (a.script || [])
        .map((b) => `<li><span class="t">${esc(b.t)}</span><span>${esc(b.beat)}</span></li>`)
        .join("");
      const v2 = (a.version || 1) > 1;
      return shell({
        ico: "🎬",
        title: `Content package · v${a.version || 1}`,
        tool: "render_content_package",
        cls: v2 ? "pass" : "",
        body: `
          <section>
            <h4>Hook ${v2 ? "· rewritten" : ""}</h4>
            <div class="hookbox">${esc(a.hook)}</div>
          </section>
          ${v2 && (a.changes || []).length
            ? `<section><h4>What changed</h4>${list(a.changes)}</section>` : ""}
          <section><h4>Script · ${esc(a.duration_s || 60)}s</h4><ul class="beats">${beats}</ul></section>
          <section><h4>Shot list</h4>${list(a.shot_list)}</section>
          <section>
            <h4>Caption</h4><p>${esc(a.caption)}</p>
            <div class="tags">${(a.hashtags || []).map((h) => `<span>${esc(h)}</span>`).join("")}</div>
          </section>
          <div class="kv">
            <span>${esc(a.platform || "tiktok")}</span>
            <span>${esc(a.package_id || "")}</span>
            <span>${esc(a.status || "")}</span>
          </div>`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_qa_verdict(a) {
      const failed = a.verdict === "fail";
      const critics = (a.critics || [])
        .map((c) => `<span>${esc(c.agent)} · ${esc(c.verdict)}</span>`)
        .join("");
      return shell({
        ico: failed ? "⛔" : "✅",
        title: `Critique · iteration ${a.iteration}/${a.max_iterations || 3}`,
        tool: "render_qa_verdict",
        cls: failed ? "fail" : "pass",
        body: `
          <section style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span class="verdict-pill ${failed ? "fail" : "pass"}">${esc(a.verdict)}</span>
            <span class="score ${a.score >= 0.7 ? "hi" : a.score >= 0.5 ? "mid" : "lo"}">${
              a.score != null ? a.score.toFixed(2) : ""
            }</span>
          </section>
          ${critics ? `<section><h4>Critics</h4><div class="kv">${critics}</div></section>` : ""}
          ${(a.issues || []).length ? `<section><h4>Issues</h4>${list(a.issues)}</section>` : ""}
          ${(a.must_fix || []).length ? `<section><h4>Must fix</h4>${list(a.must_fix)}</section>` : ""}
          ${(a.resolved || []).length ? `<section><h4>Resolved</h4>${list(a.resolved)}</section>` : ""}`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_outreach_email(a) {
      const rc = a.rate_card || {};
      const chips = Object.entries(rc)
        .map(([k, v]) => `<span>${esc(k.replace(/_/g, " "))}: ${esc(v)}</span>`)
        .join("");
      return shell({
        ico: "✉️",
        title: a.status === "sent" ? "Email · sent" : "Email · draft",
        tool: "render_outreach_email",
        cls: a.status === "sent" ? "pass" : "",
        body: `
          <div class="email">
            <div class="hdr">To: ${esc(a.to_name || "")} &lt;${esc(a.to)}&gt;</div>
            <div class="hdr">From: ${esc(a.from_name || "Maya Tan")}</div>
            <div class="subj">${esc(a.subject)}</div>
            <pre>${esc(a.body)}</pre>
          </div>
          ${chips ? `<div class="kv">${chips}</div>` : ""}
          ${(a.adapted_from || []).length
            ? `<section><h4>Adapted from memory</h4>${list(a.adapted_from)}</section>` : ""}`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_dm_script(a) {
      return shell({
        ico: "💬", title: "DM · " + (a.status || "draft"), tool: "render_dm_script",
        body: `
          <div class="email">
            <div class="hdr">${esc(a.channel)} → ${esc(a.to)}</div>
            <pre>${esc(a.message)}</pre>
          </div>
          <div class="kv"><span>send ${esc(a.scheduled_for || "now")}</span><span>${esc(a.status || "")}</span></div>`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_call_script(a) {
      const objs = (a.objections || [])
        .map((o) => `<div class="obj"><b>“${esc(o.objection)}”</b>${esc(o.response)}</div>`)
        .join("");
      return shell({
        ico: "📞", title: "Call script", tool: "render_call_script",
        body: `
          <section><h4>Opening</h4><div class="hookbox">${esc(a.opening)}</div></section>
          <section><h4>Key points</h4>${list(a.key_points)}</section>
          ${objs ? `<section><h4>Objections</h4>${objs}</section>` : ""}
          <section><h4>Close</h4><p>${esc(a.close)}</p></section>`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_calendar_week(a) {
      const days = (a.slots || [])
        .map((d) => {
          const items = (d.items || [])
            .map((i) => `<div class="slot ${esc(i.kind)}"><span class="t">${esc(i.time)}</span>${esc(i.title)}</div>`)
            .join("");
          return `<div class="day"><h3>${esc(d.day)}</h3>${items}</div>`;
        })
        .join("");
      return shell({
        ico: "📅", title: `Calendar · week of ${esc(a.week_of)}`, tool: "render_calendar_week",
        body: `<div class="calendar">${days}</div>
               <div class="kv"><span>${esc(a.timezone || "Asia/Singapore")}</span></div>`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_engagement_reply(a) {
      return shell({
        ico: "📥",
        title: `Reply · ${a.classification}`,
        tool: "render_engagement_reply",
        cls: a.classification === "interested" ? "pass" : "",
        body: `
          <div class="email">
            <div class="hdr">${esc(a.from)} · ${esc(a.channel)} · ${esc(a.received)}</div>
            <pre>${esc(a.body)}</pre>
          </div>
          <div class="kv">
            <span>${esc(a.classification)}</span>
            <span>confidence ${esc(a.confidence)}</span>
            <span>→ ${esc(a.suggested_status || "")}</span>
          </div>
          ${(a.extracted_asks || []).length
            ? `<section><h4>Extracted asks</h4>${list(a.extracted_asks)}</section>` : ""}`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_analytics(a) {
      const max = Math.max(1, ...(a.posts || []).map((p) => p.vs_median || 0));
      const bars = (a.posts || [])
        .map(
          (p) => `
          <div class="bar-row ${esc(p.verdict)}">
            <div class="lbl"><b>${esc(p.title)}</b><span>${esc(p.vs_median)}× median</span></div>
            <div class="bar"><i style="width:${Math.round(((p.vs_median || 0) / max) * 100)}%"></i></div>
          </div>`
        )
        .join("");
      return shell({
        ico: "📊", title: "Performance · " + esc(a.window), tool: "render_analytics",
        body: `<div class="bars">${bars}</div>
               <section><h4>Signal</h4><p>${esc(a.signal)}</p></section>`,
      });
    },

    /* ---------------------------------------------------------------- */
    render_plan_adaptation(a) {
      const rows = (a.changes || [])
        .map(
          (c) => `<li>
            <span class="item">${esc(c.item)}<span class="why">${esc(c.why)}</span></span>
            <span class="arrow"><s>${esc(c.before)}</s> → <b>${esc(c.after)}</b></span>
          </li>`
        )
        .join("");
      return shell({
        ico: "🧠", title: `Plan adapted · week of ${esc(a.week_of)}`, tool: "render_plan_adaptation",
        cls: "pass",
        body: `
          <section><h4>Driver</h4><p>${esc(a.driver)}</p></section>
          <section><h4>Changes</h4><ul class="deltas">${rows}</ul></section>
          <section><h4>Net effect</h4><p>${esc(a.net_effect)}</p></section>`,
      });
    },
  };

  /* Unknown tool: still render something real rather than swallowing it,
     so a new P2 tool shows up on screen the day it ships. */
  function fallback(name, args) {
    return shell({
      ico: "◫", title: name, tool: "unregistered tool",
      body: `<pre style="font:11px/1.5 var(--mono);white-space:pre-wrap;color:var(--ink-2);margin:0">${esc(
        JSON.stringify(args, null, 2)
      )}</pre>`,
    });
  }

  window.CL = { TOOLS, fallback, esc, el };
})();
