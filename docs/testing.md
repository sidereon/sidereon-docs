# Testing agents

Two kinds of tests work well together:

| Kind | Checks | Speed | Tool |
| --- | --- | --- | --- |
| Unit tests | Your wiring: tools, policies, guards, workflows | Milliseconds, no API keys | pytest + `ScriptedModel` |
| Quality tests | The answers a real model gives | Seconds to minutes | promptfoo |

## Unit tests with a scripted model

`ScriptedModel` replays prepared replies, so tests are fast and repeatable.

```python
from sidereon_adk import Agent, RolePolicy, User
from sidereon_adk.testing import ScriptedModel, tool_call

policy = RolePolicy({"issue_refund": ["lead"]})


def test_customers_do_not_see_the_refund_tool():
    model = ScriptedModel(["I can't issue refunds."])
    agent = Agent(model=model, tools=[issue_refund], policy=policy)

    agent.run("Refund A-17", user=User(id="u1", roles=["customer"]))

    assert model.calls[0]["tools"] == []  # hidden from the model


def test_leads_can_refund():
    model = ScriptedModel([tool_call("issue_refund", order_id="A-17", amount=40), "Done."])
    agent = Agent(model=model, tools=[issue_refund], policy=policy)

    response = agent.run("Refund A-17", user=User(id="u2", roles=["lead"]))

    assert response.tool_calls[0].allowed
    assert response.content == "Done."
```

`model.calls` records the messages and tools of every request for assertions.

## Quality tests with promptfoo

[promptfoo](https://promptfoo.dev) sends test prompts to your agent and checks the answers.
`promptfoo_provider` turns any agent or workflow into a promptfoo provider:

```python
# evals/promptfoo/provider.py
from sidereon_adk.evals import promptfoo_provider
from support_agent import build_support_agent

call_api = promptfoo_provider(build_support_agent)
```

```yaml
# evals/promptfoo/promptfooconfig.yaml
prompts: ["{{question}}"]
providers: [file://provider.py]
tests:
  - vars: {question: "Where is my order A-17?", roles: customer}
    assert:
      - type: icontains
        value: shipped
      - type: python
        value: file://assertions.py:used_tool
      - type: llm-rubric
        value: Polite, at most three sentences.
```

Test variables `user_id`, `roles` and `session_id` are passed to the run, so entitlement
rules are tested too. The provider returns the answer (or the typed `output`), token usage,
and metadata with the `tools` used, `blocked` and `trace_id`, which assertions can read via
`context.providerResponse.metadata`.

Run it:

```bash
make eval                                        # offline stand-in model, no keys
SIDEREON_MODEL=openai:gpt-4o-mini make eval        # real model
OPENAI_API_KEY=... make eval-live                # adds model-graded rubrics
```

The repository's suite (`evals/promptfoo/`) covers tool use, honesty about unknown data,
entitlements, prompt-injection blocking and personal-data masking.

Useful promptfoo checks for agents: `contains`/`icontains`, `regex`, `is-json` and
`contains-json` (typed output), `javascript`/`python` (custom logic), `llm-rubric`,
`answer-relevance`, `factuality`, `latency`, `cost`.

## Safety testing

See [Red-teaming](red-teaming.md) for attack suites (`make redteam-quick`, `make redteam`).

## Architecture rules

`tests/test_architecture.py` checks the rules from [Architecture](architecture.md): layers
only depend downwards, optional libraries are imported lazily, exports are sorted, and
the project uses generic names only.

## Testing policies

```bash
make policy-test     # opa fmt + opa test policies -v
```
