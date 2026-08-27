/** Patterns the trace ticker badges. Mirrors the OTEL span attribute P2 sets. */
export type Pattern = "parallel" | "sequential" | "loop" | "tool" | "custom" | "llm";

export interface Trace {
  key: string;
  agent: string;
  pattern: Pattern;
  service?: string;
  status?: "running" | "done" | "fail";
  summary: string;
}

export interface Opportunity {
  opportunity_id: string;
  type: string;
  title: string;
  score: number | null;
  status: string;
  rationale?: string;
}

export interface InboxMessage {
  id: string;
  from: string;
  channel: string;
  preview: string;
  classification: string;
}

export interface MemoryEntry {
  id: string;
  week: number;
  insight: string;
  source: string;
  confidence: number;
  changed_from?: string;
}

export interface CalendarItem {
  time: string;
  kind: string;
  title: string;
  platform?: string;
  status?: string;
}

export interface CalendarWeek {
  week_of: string;
  timezone?: string;
  slots: { day: string; items: CalendarItem[] }[];
}

export interface McpCall {
  key: string;
  server: string;
  tool: string;
  args_summary: string;
}

export interface Artifact {
  toolCallId: string;
  name: string;
  args: Record<string, unknown>;
}

export interface Board {
  running: boolean;
  runId: string | null;
  week: number;
  statusLine: string;
  traces: Trace[];
  mcp: McpCall[];
  opportunities: Opportunity[];
  calendar: CalendarWeek | null;
  inbox: InboxMessage[];
  memory: MemoryEntry[];
  artifacts: Artifact[];
}

/**
 * Pipeline statuses are owned by Pipeline Manager (8082) - this mirrors the
 * OpportunityStatus enum in shared/schemas.py. If P3 changes the enum, change
 * this list and the kanban follows.
 */
export const STATUSES: [string, string][] = [
  ["new", "New"],
  ["qualified", "Qualified"],
  ["packaged", "Packaged"],
  ["scheduled", "Scheduled"],
  ["published", "Published"],
  ["outreach_sent", "Outreach"],
  ["replied", "Replied"],
  ["negotiating", "Negotiating"],
  ["won", "Won"],
  ["lost", "Lost"],
];

export const STATUS_ALIAS: Record<string, string> = { parked: "lost" };
