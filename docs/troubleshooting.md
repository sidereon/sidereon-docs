# Troubleshooting

Find your error message below. All library errors inherit from `AgentError`.

## Set-up

`No model given. Pass model=... or set SIDEREON_MODEL.`
: Give the agent a model (`Agent(model="openai:gpt-4o-mini")`) or set the variable.

`Cannot tell which provider serves '...'. Use 'provider:model'.`
: Add the provider prefix, for example `"groq:llama-3.3-70b-versatile"`. The message lists
  all known providers. Your own provider must be registered with `register_provider`.

`OpenAI needs an api_key or set OPENAI_API_KEY.` (or another provider)
: The key is missing. Set the environment variable, pass `api_key=`, or check that the key
  exists in OpenBao if you use `use_secrets(...)`.

`... needs a base_url.`
: `OpenAICompatible` needs the server address, e.g. `base_url="http://localhost:8000/v1"`.

`ModuleNotFoundError: No module named 'qdrant_client'` (or `presidio_analyzer`, `mem0`...)
: Install the matching extra: `pip install "sidereon-adk[qdrant]"`. Each integration's
  extra is listed in its guide.

`Already inside async code: use await ...arun(...) instead of run(...).`
: You called `run()`, `batch()` or `resume()` inside an `async` function (FastAPI handler,
  notebook cell). Use `await agent.arun(...)`.

`Unknown run options: ...`
: A keyword argument was misspelled, or is not supported by that runnable (only agents
  accept `images`, `output_type` and `explain`).

## Model calls

`openai returned 401: ...` (or 403)
: The key is wrong or lacks access to that model.

`... returned 429: ...`
: Rate limited. The library already retried (`max_retries`, default 2). Lower your
  concurrency or raise your provider limits.

`Could not reach https://...`
: Network problem or wrong `base_url`. For local servers check that Ollama/vLLM is running.

`OutputError`
: The model's answer did not match your `output_type`, even after one retry. Simplify the
  type, describe fields with `Field(description=...)`, or use a stronger model.

`response.reason == "step_limit"`
: The model kept calling tools until `max_steps`. Check `response.tool_calls` for a tool
  that keeps failing, and improve tool descriptions.

## Tools and access

A tool result says `Not allowed: ...`
: The policy denied it, or a person did not approve it. `response.tool_calls[i].error` has
  the reason; with `explain=True` the explanation shows it too.

`Unknown tool '...'. Available tools: ...` in a tool result
: The model asked for a tool it cannot see — often one the policy hid for this user.

`Policy service unavailable: ...`
: OPA could not be reached. Access is denied on purpose (fail closed). Check `OPAPolicy(url)`.

`Tool names must be unique: ...`
: Two tools (often from different MCP servers) share a name. Use `MCPServer(include=[...])`
  or rename your function tool with `@tool(name=...)`.

`Invalid arguments for '...'`
: The model sent arguments that do not match the function's type hints. Clearer argument
  descriptions (`Args:` in the docstring) usually fix it.

## Workflows

`Graph '...' needs an edge from START.` / `has an edge to unknown node '...'`
: Add `graph.add_edge(START, "first_node")`, and check node names for typos.

`No route for '...' after node '...'.`
: Your condition returned a key that is not in `routes`. Add a `"default"` route.

`Graph '...' did not finish within N steps.`
: A loop never ends. Make sure your conditional edge eventually leads to `END`, or raise
  `max_steps`.

`Graph '...' join never completed; waiting for {...}`
: A `join` waits for a node that was never run (for example, a skipped branch).

## Checkpoints and approval

`Agent '...' has no checkpoint store.` / `No saved run of '...' for session '...'.`
: Pass `checkpoints=` when creating the agent, and resume with the same agent name and
  `session_id` that started the run.

A run is refused instead of pausing
: Pausing needs `checkpoints`, a `session_id`, and **no** `approve` callback.

## OpenBao

`OpenBao needs a token, an AppRole (role_id/secret_id) or a kubernetes_role.`
: Set `BAO_ROLE_ID` and `BAO_SECRET_ID` (or `BAO_TOKEN` in development).

`OpenBao refused to read secret/... (403). Check the policy attached to this login.`
: The login's policy does not allow that path. Compare with `deploy/openbao/sidereon-app.hcl`.

`Cannot reach OpenBao at ...`
: Check `BAO_ADDR`, TLS settings (`OpenBao(verify=...)`), and that OpenBao is unsealed.

## Still stuck?

Turn on `explain=True` for a step-by-step account of the run, and look at its trace using
`response.trace_id`.
