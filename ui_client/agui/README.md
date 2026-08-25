# AG-UI frontend (P4)

Kick-off stack: **AG-UI — Agentic UI. Exposing tools to agents for dynamic rendering.**

Do not stop at a chat transcript. When CDR emits a tool/artifact, render a component:

- Opportunity table
- Research brief card
- Content package (week plan + script)
- QA verdict (fail then rewrite)
- Email / DM / call script
- Calendar strip
- Memory panel

## Wire-up

1. Keep `ui_client/static/` as the no-keys fixture board.
2. Add CopilotKit here (`@copilotkit/react-core`, `@copilotkit/react-ui`, `@ag-ui/client`).
3. Point the runtime at `POST http://localhost:8084/ag-ui` (P2 AG-UI endpoint).
4. Use frontend tools so the agent can *show* a card, not only *say* JSON.

```bash
cd ui_client/agui
npm install
```

Scaffold `package.json` lists the packages. You add the Next/Vite app.
