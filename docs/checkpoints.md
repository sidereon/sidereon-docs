# Checkpoints and resume

A checkpoint is saved progress. With checkpoints, an agent or graph writes down where it is
after every step, so that:

* a run that **crashed** (network error, restart, deploy) continues from the last finished
  step instead of starting over, and
* a run can **pause** to wait for a person's approval, and continue later — minutes or days
  later, in a different process or on a different machine.

## Turn it on

```python
from sidereon_adk import Agent, FileCheckpoints

agent = Agent(
    model="openai:gpt-4o-mini", tools=[issue_refund], checkpoints=FileCheckpoints(".checkpoints")
)
response = agent.run("Refund 40 for order A-17", session_id="ticket-4711")
```

Checkpoints are used only when a `session_id` is given.

| Store | Use it for |
|---|---|
| `InMemoryCheckpoints()` | Tests and development |
| `FileCheckpoints("folder")` | One machine; survives restarts |
| `RedisCheckpoints("redis://...")` | Several processes or machines (Redis or Valkey; `ttl_seconds` to clean up) |

File and Redis stores accept `encryptor=OpenBaoTransit()` so saved runs are stored as
ciphertext; see [Secrets and encryption](secrets.md).

## Resume after a crash

```python
response = agent.resume("ticket-4711")
```

Finished model calls and tools are not repeated. If the crash happened while a tool was
running, that tool runs again, so make tools that change things safe to repeat.

## Pause for approval (human in the loop)

When a tool is marked `requires_approval=True`, the agent has checkpoints, a `session_id`
is given and there is **no** `approve` callback, the run pauses instead of refusing:

```python
response = agent.run("Refund 40 for order A-17", session_id="ticket-4711")
response.paused  # True
response.reason  # "approval_required"
response.pending  # [ToolCall(id="call_8f2", name="issue_refund", arguments={...})]

# later, anywhere (an admin page, a Slack button...):
agent.resume("ticket-4711", approvals=True)  # approve everything waiting
agent.resume("ticket-4711", approvals={"call_8f2": False})  # decide per call
```

A rejected call is reported to the model ("A person did not approve this action"), which
then answers accordingly.

## Graphs

Give the graph **and** the agents that may pause the same store:

```python
store = RedisCheckpoints("redis://cache:6379/0")
publisher = Agent("Publisher", model=..., tools=[publish_post], checkpoints=store)
graph = Graph("Blog Pipeline", checkpoints=store)
...
graph.run("topic", session_id="post-17")  # pauses inside "publish"
graph.resume("post-17", approvals=True)  # continues publish, then the next steps
```

The graph saves its position after every round. After a crash, `graph.resume()` skips the
steps that already finished.

## Good to know

* Calling `resume()` on a finished run returns the saved final response.
* Running again with the same `session_id` starts a new run and replaces the checkpoint.
* Checkpoints hold the conversation of the run, so protect the store like any other
  database containing user data — or encrypt it with an `encryptor`.
