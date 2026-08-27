import { useEffect, useState } from "react";
import { useBoard, runCampaign, stopCampaign } from "./state/store";
import {
  CampaignBar, RunStatus, AgentTrace, McpPanel, OpportunityTable,
  Kanban, CalendarStrip, InboxPanel, MemoryPanel, ArtifactDrawer,
} from "./components/panels";

export default function App() {
  const board = useBoard();
  const [niche, setNiche] = useState("home-cook / hawker-style food");
  const [city, setCity] = useState("Singapore");
  const [pause, setPause] = useState(false);
  const [mode, setMode] = useState("fixture");

  // The UI server reports whether it is replaying fixtures or proxying the
  // live CDR agent, so the badge never lies about what the judges are seeing.
  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then((cfg) => {
        setMode(cfg.mode);
        setPause(!!cfg.pause_before_send);
      })
      .catch(() => setMode("direct"));

    fetch("/api/profile")
      .then((r) => r.json())
      .then((p) => { setNiche(p.niche); setCity(p.city); })
      .catch(() => { /* keep defaults */ });
  }, []);

  return (
    <>
      <CampaignBar
        niche={niche} city={city} setNiche={setNiche} setCity={setCity}
        pause={pause} setPause={setPause} mode={mode} board={board}
        onRun={() => runCampaign({ niche, city, pauseBeforeSend: pause })}
        onStop={stopCampaign}
      />
      <RunStatus board={board} />

      <main className="board">
        <section className="col col-trace">
          <AgentTrace board={board} />
          <McpPanel board={board} />
        </section>

        <section className="col col-main">
          <OpportunityTable board={board} />
          <Kanban board={board} />
          <CalendarStrip board={board} />
          <div className="two-up">
            <InboxPanel board={board} />
            <MemoryPanel board={board} />
          </div>
        </section>

        <section className="col col-artifacts">
          <ArtifactDrawer board={board} />
        </section>
      </main>
    </>
  );
}
