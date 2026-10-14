# Explainability

Turn on `explain` to get a plain, step-by-step account of how each answer was produced:
which checks ran, what was remembered, which documents were used, which tools were hidden
or allowed, what the model asked for, and how the answer was finished.

```python
agent = Agent(model=..., tools=[...], guards=[PIIGuard()], explain=True)
# or for one run only:
response = agent.run("How much leave do I have?", user="EMP102", explain=True)

print(response.explanation.summary())
```

```text
How HR Assistant answered EMP102:
1. PIIGuard changed the request
2. Found 1 relevant passages
3. 1 of 2 tools available
4. Asked gpt-4o-mini; it requested: leave_balance
5. Ran leave_balance
6. Asked gpt-4o-mini; it answered
7. Answered
```

## What you get

`response.explanation` is an `Explanation` with:

| Field / method | Gives |
|---|---|
| `steps` | List of `Step(kind, title, details, at_ms)` |
| `of_kind("tool")` | Only the steps of one area |
| `summary()` | The numbered text above |
| `to_markdown()` | A table for audit files, tickets or review pages |
| `model_dump()` | Plain data to store in your own systems |

Step kinds: `guard`, `memory`, `knowledge`, `policy`, `model`, `tool`, `approval`,
`output`, `checkpoint`. Details hold names, counts, ids and reasons — for example which tools
the policy hid, or why a tool was not allowed — never the full prompt or answer.

## Also in your traces

The same steps are always added as events on the run's OpenTelemetry span, even without
`explain=True`, so monitoring tools show the "why" next to the timing.

## Across pauses

When a run pauses for approval and is resumed, the explanation continues where it left
off and records the approval decision.
