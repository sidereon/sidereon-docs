# Concepts

sidereon-adk helps you build AI agents: programs that use a language model to understand a
request, decide which actions (tools) to take, and answer.

## The building blocks

| Piece | What it does |
| --- | --- |
| `Agent` | A model with instructions, tools, memory, knowledge, guards and a policy |
| `tool` / `Tool` | An action the agent may take, written as a normal Python function |
| `Model` | Any language model, picked with a string like `"openai:gpt-4o-mini"` |
| `Sequential`, `Parallel`, `Router`, `Loop`, `Graph` | Ways to combine several agents |
| `Memory` / `UserMemory` | Remembers the conversation, and facts about each user across conversations |
| `Retriever` / `VectorStore` | Finds passages from your documents, in 13 vector databases |
| `Guard` | Checks the request and the answer (personal data, injection, toxicity) |
| `Policy` | Decides which tools each user may see and run (OPA) |
| `CheckpointStore` | Saves progress so runs survive crashes and can pause for approval |
| `use_secrets` / `OpenBaoTransit` | Credentials from OpenBao; stored data encrypted by OpenBao |
| `Explanation` | A step-by-step, human-readable record of each answer |
| `RedTeam` | Attacks your agent to find weaknesses |
| `Hook` | Watches each step (audit logs, costs) |
| `setup_telemetry` | Sends traces and metrics to your monitoring tools |

## What happens in a run

```text
request ─▶ input guards ─▶ load memory ─▶ search knowledge ─▶ policy hides tools
        ─▶ model ⇄ tools (policy check + approval on every call) ─▶ output guards
        ─▶ parse typed output ─▶ save memory ─▶ Response
```

Every step is traced with OpenTelemetry, and every agent and workflow shares the same
interface (`run`, `arun`, `batch`, `as_tool`), so they can be nested freely.

Next: build something in the [Tutorial](tutorial.md), or read how the pieces fit in
[Architecture and standards](architecture.md).
