const FINDER = "http://localhost:8081";
const PIPELINE = "http://localhost:8082";
const CDR = "http://localhost:8084";

const traceEl = document.getElementById("trace");
const oppsEl = document.getElementById("opps");
const memoryEl = document.getElementById("memory");

async function loadOpportunities() {
  try {
    const r = await fetch(`${FINDER}/opportunities/last`);
    const data = await r.json();
    renderOpps(data.opportunities || []);
  } catch {
    oppsEl.innerHTML = "<tr><td colspan=4>Finder not running — start services or wait for P1.</td></tr>";
  }
}

function renderOpps(rows) {
  oppsEl.innerHTML = rows
    .map(
      (o) =>
        `<tr><td>${o.type}</td><td>${o.title}</td><td>${o.score}</td><td>${o.status}</td></tr>`
    )
    .join("");
}

async function loadMemory() {
  try {
    const r = await fetch(`${PIPELINE}/pipeline/memory`);
    memoryEl.textContent = JSON.stringify(await r.json(), null, 2);
  } catch {
    memoryEl.textContent = "(pipeline manager offline)";
  }
}

function appendTrace(ev) {
  const li = document.createElement("li");
  li.textContent = `[${ev.pattern}] ${ev.agent} — ${ev.summary}`;
  traceEl.appendChild(li);
}

document.getElementById("run").addEventListener("click", async () => {
  traceEl.innerHTML = "";
  const body = {
    profile_id: "maya",
    niche: document.getElementById("niche").value,
    city: document.getElementById("city").value,
  };
  try {
    const found = await fetch(`${FINDER}/opportunities/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...body, limit: 8 }),
    }).then((r) => r.json());
    renderOpps(found.opportunities || []);
    const run = await fetch(`${CDR}/cdr/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: "maya", opportunities: found.opportunities }),
    }).then((r) => r.json());
    const es = new EventSource(`${CDR}/cdr/runs/${run.run_id}/events`);
    es.onmessage = (m) => {
      try {
        appendTrace(JSON.parse(m.data));
      } catch {
        appendTrace({ pattern: "custom", agent: "event", summary: m.data });
      }
    };
    es.onerror = () => es.close();
  } catch (err) {
    appendTrace({
      pattern: "custom",
      agent: "UI",
      summary: "Could not reach services. Showing fixture line only.",
    });
  }
});

loadOpportunities();
loadMemory();
