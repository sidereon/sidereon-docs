# Tools

Tools are actions the model can ask the agent to run.

## From a function

```python
from sidereon_adk import tool


@tool
def search_orders(customer_id: str, status: str = "open", limit: int = 10) -> list[dict]:
    """Find a customer's orders.

    Args:
        customer_id: The customer number.
        status: "open", "closed" or "all".
        limit: Maximum number of orders.
    """
```

- The name, summary and argument descriptions come from the function and its docstring.
- Type hints become the argument schema; arguments are checked before the function runs.
- `Annotated[str, "description"]` also works for argument descriptions.
- Sync and async functions both work; sync functions run in a worker thread.
- Results can be text, dicts, lists or pydantic models (turned into JSON for the model).
- Plain functions can be passed to `tools=[...]` without the decorator.

Options: `@tool(name=..., description=..., requires_approval=True, metadata={"risk": "high"})`.
`metadata` is sent to policies (OPA), so labels like risk level or owner can drive rules.

## Knowing who is asking

Add a parameter typed `RunContext`. It is filled in automatically and hidden from the model.

```python
from sidereon_adk import RunContext, tool


@tool
def my_tickets(context: RunContext) -> list[str]:
    """List my open tickets."""
    return ticket_db.open_for(context.user.id, tenant=context.user.tenant)
```

## Tool classes

For full control, subclass `Tool`:

```python
from sidereon_adk import Tool


class StockPrice(Tool):
    name = "stock_price"
    description = "Latest price of a stock ticker."

    def parameters(self):
        return {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        }

    async def call(self, arguments, context):
        return prices.latest(arguments["ticker"])
```

## Tools from an MCP server

```python
from sidereon_adk.mcp import MCPServer

server = MCPServer("http://localhost:8080/mcp", token="...", include=["create_ticket"])
agent = Agent(model="openai:gpt-4o-mini", tools=[server, my_local_tool])
```

The server's tools are listed once and cached. Their annotations (for example
`readOnlyHint`, `destructiveHint`) are kept in `tool.metadata` for your policies.

## Other agents as tools

```python
researcher = Agent("Researcher", model=..., description="Finds facts on the web.")
lead = Agent("Lead", model=..., tools=[researcher])  # name: "researcher"
lead = Agent("Lead", model=..., tools=[researcher.as_tool(name="ask_research")])
```

## Asking a person first

```python
@tool(requires_approval=True)
def send_payment(to: str, amount: float) -> str: ...


agent = Agent(model=..., tools=[send_payment], approve=lambda call, context: ask_manager(call))
```

`approve` can be sync or async and returns `True` to allow. Without `approve`, tools that
need approval are always refused.

## Order of checks for each tool call

1. The tool must exist (and must not have been hidden by the policy).
2. `policy.check(...)` must allow this user, tool and arguments.
3. If `requires_approval`, `approve(...)` must return `True`.
4. The tool runs; errors are reported back to the model.

Several tool calls requested at once run in parallel.
