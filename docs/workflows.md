# Workflows (multi-agent patterns)

Agents, the ready-made patterns and graphs all share one interface (`run`, `arun`, `batch`,
`as_tool`), so any of them can be placed inside another.

| Pattern | Use when | Class |
| --- | --- | --- |
| Pipeline | Each step builds on the previous one | `Sequential` |
| Fan-out / fan-in | Independent views of the same input, then merge | `Parallel` |
| Routing / handoff | Different requests need different specialists | `Router` |
| Reflection | Quality improves with feedback rounds | `Loop` |
| Supervisor / team | A lead decides whom to ask, and when | `Agent(tools=[other_agents])` |
| Anything else | Branches, conditions, joins, cycles | `Graph` |

## Sequential

```python
Sequential([planner, writer, editor]).run("A guide to our leave policy")
```

Stops early if a step is blocked by a guard. `response.metadata["steps"]` lists the steps run.

## Parallel

```python
Parallel([security, performance, style], combine=lead).run(design_text)
```

Branches run at the same time. Without `combine`, answers are joined under `## name`
headings; with it, the combining agent receives them and writes the final answer.
`response.metadata["outputs"]` holds each branch's answer.

## Router

```python
Router(
    {"billing": billing, "tech": tech, "general": general},
    model="openai:gpt-4o-mini",
    default="general",
).run("I was charged twice")
```

The routing model sees each route's `description`. `response.metadata["route"]` shows the choice.

## Loop (work and review)

```python
Loop(writer, critic, max_rounds=3).run("Tagline for a budgeting app")
```

The worker drafts, the reviewer responds; the draft is accepted when the review contains
`APPROVED` (or when your `approved=lambda review: ...` returns `True`). The worker sees the
feedback in the next round. `response.metadata` has `rounds` and `approved`.

## Supervisor team

```python
lead = Agent("Trip Planner", model=..., tools=[flight_agent, hotel_agent])
```

Each specialist becomes a tool named after it (customise with `.as_tool(name, description)`).
The user is passed along, so policies still apply inside specialists.

## Graph

```python
from sidereon_adk import END, START, Graph

graph = Graph("Customer Care")
graph.add_node("classify", classifier)  # agent with output_type=Intent
graph.add_node("answer", answerer)
graph.add_node("empathy", empathy)
graph.add_node("fix", fixer)
graph.add_node("reply", writer)

graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify",
    lambda state: state["intent"],
    {"question": "answer", "complaint": "empathy", "default": "answer"},
)
graph.add_edge("empathy", "fix")
graph.join(["empathy", "fix"], "reply")
graph.add_edge("answer", END)
graph.add_edge("reply", END)

graph.run("My order arrived broken!")
```

**Nodes** are agents/workflows, or functions `fn(state)` returning text, a dict (merged
into the state), or a `Response`. Functions can be async.

**State** is a dict shared by all nodes:

| Key | Holds |
| --- | --- |
| `input` | The original request |
| `content` | The latest output |
| `outputs` | `{node name: output}` |
| your keys | Values returned by function nodes, fields of an agent's `output_type`, and `state={...}` passed to `run` |

**Edges**

| Method | Behaviour |
| --- | --- |
| `add_edge(a, b)` | Run `b` after `a`. Several edges from one node run in parallel |
| `add_conditional_edges(a, fn, routes)` | `fn(state)` picks the next node, via `routes` or by returning the name |
| `join([a, b], c)` | Run `c` once both `a` and `b` finished; `c` gets their outputs combined |

Edges may point back to earlier nodes to make loops; `max_steps` (default 25) protects
against endless cycles. Each node appears as its own span in your traces.
