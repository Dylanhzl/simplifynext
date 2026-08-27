/* CreatorLoop board client.
 *
 * Speaks AG-UI over SSE from POST /ag-ui. The server decides whether those
 * events came from a fixture file or from the live CDR agent on :8084 - this
 * file never needs to know, which is what makes the day-5 swap a config change.
 */
(function () {
  "use strict";

  const { TOOLS, fallback, esc } = window.CL;
  const $ = (id) => document.getElementById(id);

  /* Pipeline statuses are owned by Pipeline Manager (8082). Mirror of the
     OpportunityStatus enum in shared/schemas.py - if P3 changes it, change
     this list and nothing else. */
  const STATUSES = [
    ["new", "New"], ["qualified", "Qualified"], ["packaged", "Packaged"],
    ["scheduled", "Scheduled"], ["published", "Published"],
    ["outreach_sent", "Outreach"], ["replied", "Replied"],
    ["negotiating", "Negotiating"], ["won", "Won"], ["lost", "Lost"],
  ];
  const STATUS_ALIAS = { parked: "lost" };

  const state = {
    runId: null, running: false, nextWeek: 1,
    opps: new Map(), traces: 0, artifacts: 0, mcp: 0,
    memory: new Map(), inbox: new Map(), startedAt: 0,
    pendingTools: new Map(),
  };

  /* ------------------------------------------------------------------ */
  /* panels                                                              */
  /* ------------------------------------------------------------------ */

  function bump(id, n) { $(id).textContent = n; }

  function addTrace(t) {
    const ul = $("trace");
    const li = document.createElement("li");
    li.className = t.status || "running";
    li.innerHTML = `
      <div class="row1">
        <span class="agent">${esc(t.agent)}</span>
        <span class="badge ${esc(t.pattern)}">${esc(t.pattern)}</span>
        <span class="svc">${esc(t.service || "")}</span>
      </div>
      <div class="summary">${esc(t.summary)}</div>`;
    ul.appendChild(li);
    ul.scrollTop = ul.scrollHeight;
    bump("trace-count", ++state.traces);
  }

  function addMcp(c) {
    const ul = $("mcp-list");
    if (state.mcp === 0) ul.innerHTML = "";
    const li = document.createElement("li");
    li.innerHTML = `<span class="tool">${esc(c.tool)}</span><span class="args">${esc(c.args_summary || "")}</span>`;
    ul.appendChild(li);
    ul.scrollTop = ul.scrollHeight;
    bump("mcp-count", ++state.mcp);
  }

  function upsertOpps(items) {
    items.forEach((o) => {
      const prev = state.opps.get(o.opportunity_id) || {};
      state.opps.set(o.opportunity_id, { ...prev, ...o });
    });
    drawOpps();
    drawKanban();
  }

  function setStatuses(updates) {
    updates.forEach((u) => {
      const o = state.opps.get(u.opportunity_id);
      if (o) o.status = u.status;
      else state.opps.set(u.opportunity_id, { opportunity_id: u.opportunity_id, title: u.opportunity_id, status: u.status, type: "—", score: null });
    });
    drawOpps();
    drawKanban();
  }

  function drawOpps() {
    const body = $("opp-body");
    const rows = [...state.opps.values()].sort((a, b) => (b.score || 0) - (a.score || 0));
    if (!rows.length) return;
    body.innerHTML = rows
      .map((o) => {
        const s = o.score;
        const cls = s == null ? "lo" : s >= 0.8 ? "hi" : s >= 0.6 ? "mid" : "lo";
        return `<tr title="${esc(o.rationale || "")}">
          <td><span class="type-chip ${esc(o.type)}">${esc(String(o.type).replace("_", " "))}</span></td>
          <td>${esc(o.title)}</td>
          <td class="num"><span class="score ${cls}">${s == null ? "—" : s.toFixed(2)}</span></td>
          <td><span class="type-chip">${esc(o.status)}</span></td>
        </tr>`;
      })
      .join("");
    bump("opp-count", rows.length);
  }

  function drawKanban() {
    const board = $("kanban");
    const buckets = new Map(STATUSES.map(([k]) => [k, []]));
    state.opps.forEach((o) => {
      const key = STATUS_ALIAS[o.status] || o.status;
      if (buckets.has(key)) buckets.get(key).push(o);
    });
    board.innerHTML = STATUSES.map(([key, label]) => {
      const items = buckets.get(key);
      const cards = items
        .map((o) => `<div class="kcard"><b>${esc(o.title)}</b>${esc(String(o.type).replace("_", " "))}</div>`)
        .join("");
      return `<div class="kcol ${esc(key)}"><h3><span>${esc(label)}</span><span>${items.length || ""}</span></h3>${cards}</div>`;
    }).join("");
  }

  function drawCalendar(a) {
    $("cal-week").textContent = "of " + a.week_of;
    $("calendar").innerHTML = (a.slots || [])
      .map((d) => {
        const items = (d.items || [])
          .map((i) => `<div class="slot ${esc(i.kind)}"><span class="t">${esc(i.time)}</span>${esc(i.title)}</div>`)
          .join("");
        return `<div class="day"><h3>${esc(d.day)}</h3>${items}</div>`;
      })
      .join("");
  }

  function drawInbox(messages) {
    messages.forEach((m) => state.inbox.set(m.id, m));
    const ul = $("inbox");
    ul.innerHTML = [...state.inbox.values()]
      .map(
        (m) => `<li>
          <div class="from"><b>${esc(m.from)}</b><span class="cls ${esc(m.classification)}">${esc(m.classification)}</span></div>
          <div class="preview">${esc(m.preview)}</div>
        </li>`
      )
      .join("");
    bump("inbox-count", state.inbox.size);
  }

  function drawMemory(entries) {
    entries.forEach((e) => state.memory.set(e.id, e));
    const ul = $("memory");
    ul.innerHTML = [...state.memory.values()].reverse()
      .map(
        (e) => `<li>
          <div>${esc(e.insight)}</div>
          <div class="meta"><span>week ${esc(e.week)}</span><span>${esc(e.source)}</span><span>conf ${esc(e.confidence)}</span></div>
          ${e.changed_from ? `<div class="was">was: <s>${esc(e.changed_from)}</s></div>` : ""}
        </li>`
      )
      .join("");
    bump("memory-count", state.memory.size);
  }

  function mountArtifact(name, args) {
    const drawer = $("artifacts");
    if (state.artifacts === 0) drawer.innerHTML = "";
    const render = TOOLS[name];
    const node = render ? render(args) : fallback(name, args);
    drawer.appendChild(node);
    // Jump, do not animate: cards can land faster than a smooth scroll
    // finishes, and each new one restarts the animation from the top.
    drawer.scrollTop = drawer.scrollHeight;
    bump("artifact-count", ++state.artifacts);
  }

  /* ------------------------------------------------------------------ */
  /* AG-UI event handling                                                */
  /* ------------------------------------------------------------------ */

  const CUSTOM = {
    agent_trace: addTrace,
    mcp_call: addMcp,
    opportunities: (v) => upsertOpps(v.opportunities || []),
    pipeline: (v) => setStatuses(v.updates || []),
    engagement: (v) => drawInbox(v.messages || []),
    memory: (v) => drawMemory(v.entries || []),
    calendar: () => {},
  };

  function handle(ev) {
    switch (ev.type) {
      case "RUN_STARTED":
        setRunning(true, ev.runId);
        break;

      case "RUN_FINISHED":
        setRunning(false);
        break;

      case "RUN_ERROR":
        status("Run error: " + (ev.message || "unknown"), "done");
        setRunning(false);
        break;

      case "CUSTOM": {
        const fn = CUSTOM[ev.name];
        if (fn) fn(ev.value || {});
        break;
      }

      case "TOOL_CALL_START":
        state.pendingTools.set(ev.toolCallId, { name: ev.toolCallName, raw: "" });
        break;

      case "TOOL_CALL_ARGS": {
        const t = state.pendingTools.get(ev.toolCallId);
        if (t) t.raw += ev.delta || "";
        break;
      }

      case "TOOL_CALL_END": {
        const t = state.pendingTools.get(ev.toolCallId);
        state.pendingTools.delete(ev.toolCallId);
        if (!t) break;
        let args = {};
        try { args = JSON.parse(t.raw || "{}"); }
        catch (e) { console.warn("bad tool args for", t.name, e); }
        mountArtifact(t.name, args);
        if (t.name === "render_calendar_week") drawCalendar(args);
        break;
      }

      case "TEXT_MESSAGE_CONTENT":
        status(ev.delta, state.running ? "running" : "done");
        break;

      default:
        break;
    }
  }

  /* ------------------------------------------------------------------ */
  /* run control                                                         */
  /* ------------------------------------------------------------------ */

  function status(text, cls) {
    $("run-status-text").textContent = text;
    $("run-status").className = "run-status " + (cls || "");
  }

  function setRunning(on, runId) {
    state.running = on;
    if (runId) state.runId = runId;
    $("btn-run").disabled = on;
    $("btn-stop").disabled = !on;
    if (on) {
      state.startedAt = Date.now();
      tick();
    } else {
      $("run-meta").textContent =
        `${state.traces} agent steps · ${state.artifacts} artifacts · ${((Date.now() - state.startedAt) / 1000).toFixed(1)}s`;
      state.nextWeek = state.nextWeek === 1 ? 2 : 1;
      $("btn-run").textContent = state.nextWeek === 2 ? "Run week 2 (replay)" : "Run campaign";
      if (state.nextWeek === 2) status("Week 1 done. Week 2 replays what came back.", "done");
    }
  }

  function tick() {
    if (!state.running) return;
    $("run-meta").textContent =
      `run ${state.runId || "…"} · ${((Date.now() - state.startedAt) / 1000).toFixed(1)}s · ${state.traces} steps`;
    setTimeout(tick, 200);
  }

  async function run() {
    const week = state.nextWeek;
    if (week === 1) {
      // Fresh week 1 clears the board; week 2 must build on week 1's state.
      state.opps.clear(); state.memory.clear(); state.inbox.clear();
      state.traces = 0; state.artifacts = 0; state.mcp = 0;
      $("trace").innerHTML = ""; $("artifacts").innerHTML = "";
      $("mcp-list").innerHTML = '<li class="empty">No tool calls yet.</li>';
      ["trace-count", "artifact-count", "mcp-count", "opp-count", "inbox-count", "memory-count"].forEach((i) => bump(i, 0));
    }

    const runId = `run_${Date.now().toString(36)}`;
    state.runId = runId;
    setRunning(true, runId);
    status(week === 1 ? "Running campaign…" : "Replaying week 2…", "running");

    const payload = {
      runId, week,
      threadId: "maya",
      profile: "maya",
      niche: $("f-niche").value,
      city: $("f-city").value,
      pause_before_send: $("f-pause").checked,
    };

    let res;
    try {
      res = await fetch("/ag-ui", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      status("Cannot reach the UI server on :8000.", "done");
      setRunning(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      let idx;
      while ((idx = buf.indexOf("\n\n")) !== -1) {
        const frame = buf.slice(0, idx);
        buf = buf.slice(idx + 2);
        for (const line of frame.split("\n")) {
          if (!line.startsWith("data:")) continue;
          const payloadText = line.slice(5).trim();
          if (!payloadText) continue;
          try { handle(JSON.parse(payloadText)); }
          catch (e) { console.warn("bad SSE frame", payloadText, e); }
        }
      }
    }

    if (state.running) setRunning(false);
  }

  async function stop() {
    $("btn-stop").disabled = true;
    status("Stopping…", "running");
    await fetch("/api/stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ runId: state.runId }),
    }).catch(() => {});
  }

  /* ------------------------------------------------------------------ */

  async function boot() {
    drawKanban();
    try {
      const cfg = await (await fetch("/api/config")).json();
      const badge = $("mode-badge");
      badge.textContent = cfg.mode === "live" ? "live · :8084" : "fixture mode";
      badge.className = "mode-badge " + cfg.mode;
      badge.title = cfg.mode === "live"
        ? `Streaming from ${cfg.cdr_agui_url}`
        : "Replaying demo/fixtures - no LLM keys needed";
      $("f-pause").checked = !!cfg.pause_before_send;
    } catch (e) {
      $("mode-badge").textContent = "offline";
    }
    try {
      const p = await (await fetch("/api/profile")).json();
      $("f-niche").value = p.niche;
      $("f-city").value = p.city;
    } catch (e) { /* keep the defaults in the markup */ }
  }

  $("btn-run").addEventListener("click", run);
  $("btn-stop").addEventListener("click", stop);
  boot();
})();
