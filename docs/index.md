---
myst:
  html_meta:
    description: "sidereon-adk: build AI agents and multi-agent workflows in Python with any model, OPA entitlements, OpenTelemetry and promptfoo."
---

# sidereon-adk

```{rst-class} hero-tagline
```
Build AI agents and multi-agent workflows in Python — with any model, safe by default,
observable with OpenTelemetry, and testable from day one.

```python
from sidereon_adk import Agent, tool


@tool
def get_order_status(order_id: str) -> str:
    """Look up the status of an order."""
    return "shipped"


agent = Agent(model="openai:gpt-4o-mini", tools=[get_order_status])
print(agent.run("Where is order A-17?").content)
```

```bash
pip install sidereon-adk
```

## Where to go next

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`rocket` Get started
:link: getting-started
:link-type: doc

Install, configure a model, and run your first agent in five minutes.
:::

:::{grid-item-card} {octicon}`mortar-board` Tutorial
:link: tutorial
:link-type: doc

Build a complete support agent step by step: tools, memory, safety, access rules, tests.
:::

:::{grid-item-card} {octicon}`book` Guides
:link: agents
:link-type: doc

Every feature explained: models, tools, workflows, memory, knowledge, guards and more.
:::

:::{grid-item-card} {octicon}`code-square` Examples
:link: examples/index
:link-type: doc

31 runnable programs covering every feature and multi-agent pattern.
:::

:::{grid-item-card} {octicon}`file-code` API reference
:link: reference/index
:link-type: doc

Every public class and function, generated from the source code.
:::

:::{grid-item-card} {octicon}`stack` Architecture & standards
:link: architecture
:link-type: doc

How the library is built, and the rules that keep it simple and safe.
:::
::::

## What you get

| | |
|---|---|
| **Any model** | OpenAI, Anthropic, Gemini, Azure, Groq, Mistral, DeepSeek, OpenRouter, Ollama, vLLM, your own |
| **Multi-agent patterns** | Sequential, parallel, router, review loop, supervisor teams, custom graphs |
| **Safe by default** | OPA entitlements, guards (Presidio, LlamaFirewall, Prompt Guard), human approval, red-teaming |
| **Production ready** | Checkpoints and resume, OpenBao secrets and encryption, Valkey memory, OpenTelemetry |
| **Grounded answers** | Document loading, 8 embedding providers, 13 vector databases |
| **Testable** | Scripted models for unit tests, promptfoo quality suites, explainability reports |

```{toctree}
:hidden:
:caption: Get started

getting-started
tutorial
concepts
```

```{toctree}
:hidden:
:caption: Guides

agents
tools
models
workflows
memory
knowledge
guards
policy
secrets
checkpoints
explainability
observability
```

```{toctree}
:hidden:
:caption: Quality and safety

testing
red-teaming
```

```{toctree}
:hidden:
:caption: Production

production
troubleshooting
```

```{toctree}
:hidden:
:caption: Build on it

extending
architecture
development
writing-docs
```

```{toctree}
:hidden:
:caption: Reference

examples/index
reference/index
changelog
```
