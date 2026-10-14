# Getting started

## Install

```bash
pip install sidereon-adk
# optional extras
pip install "sidereon-adk[otel]"    # OpenTelemetry exporters
pip install "sidereon-adk[redis]"   # Redis / Valkey memory
```

Python 3.10 or newer is required.

## Your first agent

```python
from sidereon_adk import Agent

agent = Agent(
    name="Assistant",
    model="openai:gpt-4o-mini",
    instructions="Explain things simply.",
)
print(agent.run("What is a vector database?").content)
```

Set the API key for your provider as an environment variable (`OPENAI_API_KEY`,
`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, ...). See [Models](models.md) for the full list.

## Configuration

Settings come from arguments first and environment variables second. Copy `.env.example`
to `.env` for a complete list. The most useful one:

| Variable | Meaning |
| --- | --- |
| `SIDEREON_MODEL` | Default model when an agent has no `model=` (e.g. `anthropic:claude-sonnet-5-5`) |

## Add a tool

```python
from sidereon_adk import Agent, tool


@tool
def get_order_status(order_id: str) -> str:
    """Look up the status of an order.

    Args:
        order_id: The order number, for example A-17.
    """
    return "shipped"


agent = Agent(model="openai:gpt-4o-mini", tools=[get_order_status])
response = agent.run("Where is order A-17?")
print(response.content)
print(response.tool_calls)  # what was called, with which arguments, and the result
```

## Next steps

- [Agents](agents.md) for all options
- [Workflows](workflows.md) to combine agents
- [Tutorial](tutorial.md) to build a complete agent step by step
- [Examples](examples/index.md) for runnable code
