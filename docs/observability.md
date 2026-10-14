# Observability (OpenTelemetry)

Every run is traced with [OpenTelemetry](https://opentelemetry.io/), the open standard
supported by almost every monitoring tool: Jaeger, Grafana Tempo, Honeycomb, Datadog,
New Relic, Dynatrace, Azure Monitor, AWS X-Ray, Google Cloud Trace and more.
No vendor-specific tracing SDK is needed.

## Turn it on

```python
from sidereon_adk import setup_telemetry

setup_telemetry(
    "support-bot",  # service name
    exporter="otlp",  # "otlp", "console" or "none"
    endpoint="http://localhost:4318",  # default: OTEL_EXPORTER_OTLP_ENDPOINT
    headers={"x-api-key": "..."},  # if your backend needs one
    capture_content=False,  # True also records prompts and answers
)
```

Requires `pip install "sidereon-adk[otel]"`. If your application already configures
OpenTelemetry, skip `setup_telemetry`; spans and metrics flow into your existing setup.

Try it locally: `docker compose -f deploy/docker-compose.yml up jaeger`, then open
`http://localhost:16686`.

## What is recorded

A run produces a tree like this:

```text
invoke_agent Support Bot                 user, session, total tokens, blocked
├── policy allowed_tools                 tools the user may see
├── chat gpt-4o-mini                     provider, model, tokens, requested tools
├── execute_tool get_order_status        outcome: ok | error | denied
│   └── policy check                     allowed or not
└── chat gpt-4o-mini
```

Workflows add `workflow <name>` and `node <name>` spans around their agents.
Errors are marked on the span where they happened.

Attribute names follow the OpenTelemetry conventions for AI applications
(`gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, ...), so
AI-aware dashboards understand them without extra mapping.

### Metrics

| Metric | Type | Labels |
| --- | --- | --- |
| `gen_ai.client.token.usage` | histogram | provider, model, token type (input/output) |
| `gen_ai.client.operation.duration` | histogram (seconds) | provider, model |
| `sidereon.tool.calls` | counter | tool, outcome |

### Prompts and answers

Off by default because they can contain personal data. Turn on with
`capture_content=True` or `SIDEREON_CAPTURE_CONTENT=true`; they are then added to model and
tool spans.

## Linking to your logs

`response.trace_id` is the id of the run's trace. Log it alongside your own records to jump
from a log line or support ticket straight to the trace. For audit trails or cost tracking
in code, use [hooks](extending.md#hooks).
