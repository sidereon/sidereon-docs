# Extending

Every part of the library is an interface with a simple default. Swap in your own without
touching anything else. Step-by-step checklists are in [Architecture](architecture.md#9-checklists).

| Replace | Subclass | Implement |
| --- | --- | --- |
| Model | `sidereon_adk.models.Model` | `async generate(messages, tools)`, optional `async stream(messages)` |
| Tool | `sidereon_adk.Tool` | `parameters()`, `async call(arguments, context)` |
| Group of tools | `sidereon_adk.tools.Toolset` | `async tools()` |
| Conversation memory | `sidereon_adk.memory.Memory` | `async load`, `async save`, `async clear` |
| User memory | `sidereon_adk.memory.UserMemory` | `async recall`, `async remember`, `async forget` |
| Knowledge | `sidereon_adk.knowledge.Retriever` | `async search(query, k)` |
| Embeddings | `sidereon_adk.knowledge.Embedder` | `async embed(texts)` |
| Vector database | `sidereon_adk.knowledge.stores.VectorStore` | `async add`, `async search`, `async delete` |
| Guard | `sidereon_adk.Guard` | `async check_input` and/or `async check_output` |
| Personal-data guard | `sidereon_adk.guards.MaskingGuard` | `async find(text)` |
| Checkpoint store | `sidereon_adk.checkpoints.CheckpointStore` | `async save`, `async load`, `async delete` |
| Policy | `sidereon_adk.policy.Policy` | `async check(tool, arguments, context)`, optional `allowed_tools` |
| Hook | `sidereon_adk.Hook` | any of the `on_*` methods |
| Workflow | `sidereon_adk.Runnable` | `async _run(input, context, **options) -> Response` |

Plain functions are accepted wherever it makes sense: tools, custom models
(`CustomModel(fn)`), approval callbacks and graph nodes/conditions, sync or async.

## Hooks

Hooks observe each step without changing it; ideal for audit logs, cost tracking and alerts.

```python
from sidereon_adk import Hook


class AuditLog(Hook):
    async def on_tool_end(self, context, record):
        audit.write(
            user=context.user.id,
            run=context.run_id,
            tool=record.name,
            allowed=record.allowed,
            error=record.error,
        )


agent = Agent(model=..., hooks=[AuditLog()])
```

| Method | Called |
| --- | --- |
| `on_run_start(context, input)` | when a run begins |
| `on_model_start(context, messages)` | before each model call |
| `on_model_end(context, reply)` | after each model call (has token usage) |
| `on_tool_start(context, call)` | before a tool runs (after policy and approval) |
| `on_tool_end(context, record)` | after a tool finished, failed or was denied |
| `on_run_end(context, response)` | with the final response |

## A new workflow pattern

```python
from sidereon_adk import Response, Runnable


class FirstGoodAnswer(Runnable):
    """Try agents in order until one answers without being blocked."""

    def __init__(self, agents, name="first-good"):
        self.agents, self.name = agents, name

    async def _run(self, input, context, **options):
        for agent in self.agents:
            response = await agent.arun(input, user=context.user, session_id=context.session_id)
            if not response.blocked:
                return response
        return Response(content="No agent could answer.", blocked=True)
```

It is traced, batchable, nestable and usable as a tool automatically.
