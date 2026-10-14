# API reference

Generated from the source code's docstrings. Most names are also importable directly from
`sidereon_adk` (for example `from sidereon_adk import Agent, tool, OPAPolicy`).

| Area | Covers |
|---|---|
| [Agents and results](agents.md) | The agent, the shared runnable interface, and what a run returns. |
| [Tools](tools.md) | Turning functions into tools, tool classes, and tools from MCP servers. |
| [Models](models.md) | The model interface, the provider picker and every built-in provider. |
| [Workflows and graphs](workflows.md) | Ready-made multi-agent patterns and custom graphs. |
| [Memory](memory.md) | Conversation memory and long-term user memory. |
| [Knowledge](knowledge.md) | Documents, keyword and vector search, embeddings and vector databases. |
| [Guards and policies](safety.md) | Safety and personal-data guards, and entitlement policies. |
| [Operations](operations.md) | Checkpoints, secrets, encryption, OpenBao, telemetry, explanations and hooks. |
| [Testing and safety testing](testing.md) | Scripted models, the promptfoo provider and red-teaming. |

```{toctree}
:hidden:

agents
tools
models
workflows
memory
knowledge
safety
operations
testing
```
