# sidereon-docs

Developer documentation for **sidereon-adk**, published at
**https://sidereon.github.io/sidereon-docs/**.

## How the docs stay in sync with the SDK

| Lives here (`sidereon-docs`) | Comes from `sidereon-adk` at build time |
|---|---|
| Guides, tutorial, architecture, every page in `docs/` | API reference (from the code's docstrings) |
| Site settings (`docs/conf.py`) and the publishing workflow | Example pages, changelog, sample OPA policy |

The site is rebuilt and published:

- on every push to `main` here (docs changes),
- every night (picks up SDK changes),
- any time from **Actions → Publish docs → Run workflow**.

Describe functions in their **docstrings** in `sidereon-adk`; write guides **here**.
No SDK source code is published.

## Preview locally

Clone both repositories side by side, then:

```bash
git clone https://github.com/sidereon/sidereon-adk.git ../sidereon-adk   # if not there yet
make install       # .venv with the SDK and the documentation tools
make docs          # live preview at http://127.0.0.1:8000
make docs-build    # strict build, as published
```

See `docs/writing-docs.md` for writing tips.
