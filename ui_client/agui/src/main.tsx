import React from "react";
import { createRoot } from "react-dom/client";
import { CopilotKitProvider, CopilotSidebar } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

import App from "./App";
import { AGENTS } from "./agui/agent";
import { CARDS } from "./components/cards";

// The board and the static fallback share one stylesheet, so both surfaces
// stay visually identical as the design changes.
import "../../static/styles.css";
import "./agui.css";

/**
 * Every render tool the CDR agent can call is registered with CopilotKit, so
 * a tool call made from the chat thread mounts the same component the artifact
 * drawer uses. Unregistered tools still render through UnknownCard - a new P2
 * tool shows up on screen the day it ships instead of vanishing.
 */
const renderToolCalls = Object.entries(CARDS).map(([name, Card]) => ({
  name,
  render: ({ args }: { args: any }) => <Card a={args ?? {}} />,
}));

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <CopilotKitProvider
      // Dev/demo wiring: the browser talks to the AG-UI endpoint directly, so
      // there is no extra runtime process to keep alive during the demo.
      agents__unsafe_dev_only={AGENTS}
      renderToolCalls={renderToolCalls as any}
    >
      <App />
      {/* Chat is the secondary surface: the board is the demo, the sidebar is
          there so a judge can ask the agent for something ad hoc and watch the
          same card components render inline. */}
      <CopilotSidebar
        agentId="cdr"
        defaultOpen={false}
        width={420}
        labels={{ chatInputPlaceholder: "Ask the CDR agent…" } as any}
      />
    </CopilotKitProvider>
  </React.StrictMode>
);
