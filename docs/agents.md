# Agents

```python
Agent(
    name="Support Agent",
    model="openai:gpt-4o-mini",  # Model object or "provider:model"
    instructions="...",  # role and behaviour
    description="...",  # one line, used when other agents call this one
    tools=[...],  # functions, Tool objects, MCP servers, other agents
    memory=InMemory(),  # remembers conversations (needs session_id)
    user_memory=LocalUserMemory(),  # facts about each user, across conversations
    knowledge=retriever,  # adds relevant passages to each request
    knowledge_results=4,
    guards=[PIIGuard()],  # checks on the request and the answer
    policy=OPAPolicy(...),  # who may see/run which tools
    hooks=[AuditLog()],  # observers of every step
    output_type=MyModel,  # typed answers
    max_steps=10,  # limit on model calls per run
    approve=ask_a_person,  # for tools marked requires_approval
    checkpoints=FileCheckpoints(),  # save progress; resume after crashes or pauses
    explain=True,  # attach a step-by-step explanation
    blocked_message="Sorry, I can't help with that request.",
)
```

## Running

| Method | Use it for |
| --- | --- |
| `run(text, ...)` | Normal Python code |
| `await arun(text, ...)` | Async code (web servers, notebooks) |
| `stream(text)` / `astream(text)` | Show the answer as it is written |
| `batch([...])` / `abatch([...])` | Many requests at once (`max_concurrency=4`) |
| `resume(session_id, approvals=...)` | Continue a saved run (see [Checkpoints](checkpoints.md)) |

Common arguments for all of them:

| Argument | Meaning |
| --- | --- |
| `user` | A `User(id, roles, scopes, tenant, attributes)` or just an id string |
| `session_id` | Turns on memory for this conversation |
| `metadata` | Extra values passed to tools, guards, policies and hooks |
| `images` | Image URLs or `data:` URLs (agents only) |
| `output_type` | Override the typed output for this run (agents only) |
| `explain` | Turn the explanation on or off for this run (agents only) |

```{note}
`run()` cannot be called from inside async code; use `await agent.arun(...)` there.
```

## The response

```python
response.content  # the answer text
response.output  # typed object when output_type is set
response.tool_calls  # list of ToolRecord(name, arguments, result, allowed, error)
response.sources  # documents used from knowledge
response.usage  # input_tokens, output_tokens, total_tokens
response.blocked  # True when a guard stopped the run
response.paused  # True when waiting for a person's approval
response.pending  # the tool calls waiting for approval
response.reason  # why it was blocked or paused, or "step_limit"
response.explanation  # step-by-step record (with explain=True)
response.trace_id  # find this run in your tracing tool
```

## Typed answers

```python
from pydantic import BaseModel


class Ticket(BaseModel):
    category: str
    urgent: bool


ticket = Agent(model="openai:gpt-4o-mini", output_type=Ticket).run("Charged twice!").output
```

The model is asked to reply in JSON that matches the type. If the reply cannot be read, it
is asked once more; if it still fails, `OutputError` is raised. Any type works:
`list[str]`, `dict[str, int]`, dataclasses, `Literal[...]`.

## Errors when things go wrong

| Situation | What happens |
| --- | --- |
| Tool raises an error | The error text is given to the model so it can recover |
| Unknown tool requested | The model is told which tools exist |
| Policy denies a tool call | The model is told it is not allowed; `ToolRecord.allowed=False` |
| Step limit reached | `response.reason == "step_limit"` |
| Model provider fails | `ModelError` (after automatic retries for busy/temporary errors) |
| Bad configuration | `ConfigError` |

All errors inherit from `AgentError`.
