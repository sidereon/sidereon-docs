# Development workflow

How to work on sidereon-adk itself. Read [Architecture and standards](architecture.md) first:
it explains the structure and the rules every change follows.

## Set up

```bash
git clone <repository> && cd sidereon-adk
make install          # .venv with Python, dev tools and git hooks (needs uv)
make check            # everything CI runs
```

Optional local services (OPA, Jaeger, Valkey, OpenBao):

```bash
docker compose -f deploy/docker-compose.yml up
```

## Everyday commands

| Command | What it does |
|---|---|
| `make format` | Format code and fix simple style issues (ruff) |
| `make lint` | Fail on any formatting or style problem |
| `make typecheck` | Static type checks (mypy) |
| `make test` | Unit tests with coverage; fails under 90% |
| `make policy-test` | Format check and tests for the OPA policies |
| `make eval` | promptfoo quality suite (offline stand-in model unless `SIDEREON_MODEL` is set) |
| `make redteam-quick` | Built-in attack suite against the sample agent |
| `make check` | All of the above checks, as in CI |

Git hooks (`pre-commit`) run ruff and mypy before each commit.

## Making a change

1. Find the right place using the [layer rules](architecture.md#7-dependency-rules-who-may-use-whom)
   and the [checklists](architecture.md#9-checklists).
2. Write tests first where possible. No network: use `ScriptedModel`,
   `httpx.MockTransport` and stand-in clients.
3. Keep the public API small; export new public names from the package `__init__` and keep
   `__all__` sorted.
4. Add or update an example in `examples/` and a line in `CHANGELOG.md`; write docstrings
   for new public names (they become the API reference). Update or add the guide in the
   `sidereon-docs` repository.
5. Run `make check`. `tests/test_architecture.py` enforces several standards automatically.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

| Job | Runs |
|---|---|
| checks | lint, type check and tests on Python 3.10, 3.12 and 3.13 |
| policies | OPA formatting and tests |
| quality | promptfoo suite and red-team suite with the offline model |

The documentation is built and published by the `sidereon-docs` repository, which reads this
repository's `main` branch every night (see [Writing and publishing docs](writing-docs.md)).

## Releasing

1. Move the "Unreleased" notes in `CHANGELOG.md` under the new version.
2. Update `version` in `pyproject.toml` — the only place it is written; the package reads it
   from there at run time.
3. `uv run --no-sync python -m build` and publish the wheel to your package index.
4. Tag the release, then run **Actions → Publish docs → Run workflow** in `sidereon-docs`
   to publish the documentation immediately (otherwise it updates overnight).

Versions follow semantic versioning; see
[Public API and versions](architecture.md#811-public-api-and-versions).
