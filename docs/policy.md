# Policies (entitlements with OPA)

A policy decides **which tools each user can see** and **whether a specific tool call is
allowed**. Rules live in [Open Policy Agent](https://www.openpolicyagent.org/), so they are
central, versioned and testable, and the same rules can serve many agents.

```python
from sidereon_adk import Agent, OPAPolicy, User

agent = Agent(
    model="openai:gpt-4o-mini",
    tools=[get_order_status, issue_refund, delete_customer],
    policy=OPAPolicy("http://localhost:8181", package="sidereon.tools"),
)
agent.run("Refund 900 for A-17", user=User(id="EMP102", roles=["support_lead"], tenant="acme"))
```

## How it works

1. **Before the model is called**, OPA's `allowed_tools` rule receives the user and the
   list of tools. Only the tools it returns are shown to the model.
2. **Before every tool call**, OPA's `allow` rule receives the user, the tool and the exact
   arguments. A denied call is not run; the model is told it is not allowed.
3. **If OPA cannot be reached, everything is denied.**

### What OPA receives

`POST {url}/v1/data/sidereon/tools/allowed_tools`

```json
{"input": {
  "user": {"id": "EMP102", "roles": ["support_lead"], "scopes": [], "tenant": "acme", "attributes": {}},
  "tools": [{"name": "issue_refund", "description": "...", "requires_approval": false,
             "metadata": {"risk": "medium"}}]
}}
```

`POST {url}/v1/data/sidereon/tools/allow`

```json
{"input": {
  "user": {"id": "EMP102", "roles": ["support_lead"], "scopes": [], "tenant": "acme", "attributes": {}},
  "tool": {"name": "issue_refund", "description": "Refund money for an order.",
           "requires_approval": false, "metadata": {"risk": "medium"}},
  "arguments": {"order_id": "A-17", "amount": 900},
  "session_id": "chat-1",
  "metadata": {}
}}
```

`allowed_tools` returns a list of names (or tool objects). `allow` returns `true`/`false`
or `{"allow": false, "reason": "Refunds above 500 need an admin"}`; the reason is passed
to the model and recorded on the trace.

## Sample policy

`policies/tools.rego` shows role-based access, an argument rule (refund limit) and a
metadata rule (high-risk tools are admin-only):

```{literalinclude} _from_adk/tools.rego
:language: rego
```

Its tests are in `policies/tools_test.rego`:

```bash
opa test policies -v                                   # or: make policy-test
opa run --server --addr :8181 policies/                # or: docker compose ... up opa
```

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `url` | `http://localhost:8181` | OPA server |
| `package` | `sidereon.tools` | Rego package that holds `allow` and `allowed_tools` |
| `filter_tools` | `True` | Set `False` to show every tool and only check at call time |
| `timeout` | `5` | Seconds |

## Without an OPA server

`RolePolicy` keeps simple role rules in code (handy for development and tests):

```python
RolePolicy({"get_order_status": ["*"], "issue_refund": ["support_lead", "admin"]})
```

Write your own by subclassing `Policy` and implementing `async check(tool, arguments, context)`
(and optionally `allowed_tools`).
