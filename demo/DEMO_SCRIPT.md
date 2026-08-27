# CreatorLoop — 3:00 demo script

Recorded from the UI at **http://localhost:8000** (or the AG-UI client on :5173).
Run with `DEMO_SPEED=0.6` — every cue below is measured against that setting.

```bash
DEMO_SPEED=0.6 python3 ui_client/server.py
```

One browser tab. One human action in the whole video: the **Run campaign** button,
clicked twice.

---

## Setup before you hit record

- Window at 1600×1000 or wider, so all three columns fit.
- Board idle, nothing run yet. Mode badge reads `FIXTURE MODE` (or `LIVE · :8084` on day 5).
- CopilotKit sidebar closed. The board is the demo.
- Have `demo/maya/profile.json` open in a second tab if a judge asks who Maya is.

---

## 0:00 — 0:25 · The problem

> "This is Maya. She cooks hawker food in an HDB kitchen for about eight thousand
> people. She wants three posts a week and one small brand deal.
>
> Right now every week starts from a blank page. Find the trend, write the hook,
> shoot it, caption it, then cold-email a stall owner who has never heard of her.
> It's four hours of admin before any cooking happens, so two of the three posts
> never get made."

**On screen:** the idle board. Campaign bar with niche, city, Maya, and one button.

> "The kick-off brief asked for something that plans, acts, and adapts over time.
> That's the whole job here."

---

## 0:25 — 0:50 · The architecture

**On screen:** stay on the board, point at the left and right columns.

> "CreatorLoop is five services and a shared MCP tool server. An Opportunity
> Finder, a CDR orchestrator running LangGraph graphs under a DeepAgents root,
> a Pipeline Manager, an Engagement Listener, and this UI.
>
> Thirty-nine named agents run across them. Not one mega-prompt — every one of
> them shows up by name on the left with the pattern it uses: parallel,
> sequential, loop, tool, custom, llm. Those are the OpenTelemetry span names,
> on screen, live.
>
> The human's job is one click."

---

## 0:50 — 1:20 · Run the campaign, parallel research

**Click `Run campaign`.**

| Cue | What lands |
|---|---|
| 0:52 | `FinderFanoutAgent` · **parallel** — four scouts start at once |
| 0:55 | MCP panel lights up: `search`, `places` |
| 1:01 | Opportunity table fills with 6 scored rows |
| 1:09 | **Research brief card** renders in the artifact drawer |
| 1:15 | **Content package v1** card renders |

> "One click. Four scouts fan out in parallel — trends, brand gaps, collabs, and
> a places lookup through MCP. They gather, dedupe fourteen candidates down to
> six, and score them against Maya's voice.
>
> Top of the board: laksa in sixty seconds. Her best-ever post was laksa.
>
> Now watch the right column. These are not chat messages. The agent calls a
> render tool, and AG-UI mounts a real component — a research brief, then a
> full content package with hook, script beats, shot list and caption."

---

## 1:20 — 1:40 · Critique fails, then the rewrite

| Cue | What lands |
|---|---|
| 1:18 | `HookCriticAgent` · **loop** turns red — status `fail` |
| 1:20 | **Critique card, iteration 1/3 — FAIL 0.42** |
| 1:24 | **Content package v2** with the rewritten hook |
| 1:27 | **Critique card, iteration 2/3 — PASS 0.86** |

> "And here's the part I actually care about. Three critics review that package.
> Brand safety passes. Fact-check flags an unverifiable claim. The hook critic
> fails it outright — score 0.42.
>
> Look at the reasons: 'Hey guys' is a generic greeting, 'best laksa in
> Singapore' is unverifiable, and nothing places it in Tiong Bahru. Three
> must-fix items, structured, not vibes.
>
> The rewrite agent takes another pass — iteration two of a max of three."

**Point at the v2 hook.**

> "'My neighbours queue forty minutes for this bowl. I'm making it in my HDB
> kitchen for four dollars.' Concrete, checkable, no superlatives. 0.86, pass.
>
> Nobody approved that. The loop caught its own bad work and fixed it."

---

## 1:40 — 2:00 · Outreach goes out on its own

| Cue | What lands |
|---|---|
| 1:40 | **Email card — sent**, Laksa Lab, SGD 650 rate card |
| 1:42 | **DM card — queued** for Wednesday 10:00 |
| 1:45 | **Call script card** with three objection handles |
| 1:46 | `SendGateAgent` · custom — "PAUSE_BEFORE_SEND is off. Sent 1 email, queued 1 DM." |

> "Outreach writes itself. A real email to the stall owner with a rate card
> benchmarked against local micro-creator rates, a DM as the Wednesday nudge,
> and a call script with objection handles for when she walks in.
>
> That email is sent. There is a pause-before-send toggle and it is off by
> default, because supervising an agent shouldn't mean approving every sentence
> it writes."

---

## 2:00 — 2:15 · Pipeline and calendar

**Pan to the centre column.**

> "Everything persisted. The pipeline kanban is the Pipeline Manager's own
> statuses — new, qualified, packaged, scheduled, outreach sent.
>
> And the week is booked: three posts on Maya's actual filming days. The slot
> optimiser moved Thursday from noon to seven, because that's when her audience
> is awake.
>
> That's plan and act. Now the part most demos skip."

---

## 2:15 — 2:45 · Week 2 — what came back changes the plan

**Click `Run week 2 (replay)`.**

| Cue | What lands |
|---|---|
| 2:24 | **Reply card** — Wei Sheng, Laksa Lab, classified `interested` 0.92 |
| 2:26 | **Analytics card** — laksa 3.1× median, dessert 0.4× |
| 2:31 | `MemoryAdaptAgent` · **loop** — "3 entries updated, 1 promoted to a hard rule" |
| 2:37 | **Plan adapted card** — before → after weights |
| 2:41 | Calendar replans to the week of Sep 7 |
| 2:44 | **Counter-offer email — sent** |

> "A week passes. The brand replied — interested, but asks for two posts instead
> of three, and a weekday morning shoot. Analytics land: the laksa post did
> three times her median. The dessert test did four tenths.
>
> Watch the memory panel. 'Dessert scores minus 0.20 and is no longer proposed'
> — that was a soft observation last week, it's a hard rule now. And the hook
> lesson is confirmed: zero rewrite loops this run.
>
> Then the plan changes by itself. Dessert drops off the board. The Laksa Lab
> shoot moves to Wednesday morning because the brand asked. And the counter-offer
> — two posts, SGD 450, third post as an upsell — is already sent."

---

## 2:45 — 3:00 · Closer

> "Plan: it found and scored the week's work.
> Act: it wrote, critiqued, rewrote, scheduled, and sent.
> Adapt: what came back rewrote next week's plan without anyone asking.
>
> Thirty-nine named agents, six patterns, MCP tools, AG-UI components, OTEL
> spans — and one button. That's CreatorLoop."

---

## If something breaks mid-record

- **Board empty after clicking Run** — the server isn't up. `python3 ui_client/server.py`, reload.
- **Live mode and P2 is down** — the trace shows `RunSupervisor` saying it fell back to
  fixtures, and the story still runs. Don't stop recording.
- **Run too fast to narrate** — raise `DEMO_SPEED` above 1.0 to speed up, lower it to slow down.
  0.6 is the setting these cues are measured at; 0.45 gives you a slower, 90-second week 1.
