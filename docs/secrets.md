# Secrets and encryption (OpenBao)

[OpenBao](https://openbao.org) is an open-source secrets manager. sidereon-adk uses it for
the two jobs it is built for:

1. **Secrets** — API keys and tokens live in OpenBao, not in code, `.env` files or images.
2. **Encryption** — conversations and checkpoints are encrypted by OpenBao before they are
   written to Valkey/Redis or disk, so those stores only hold ciphertext.

Valkey stays the place where conversations and checkpoints are kept.

## Why OpenBao and Valkey are used together

They solve different problems, so one does not replace the other.

| | Valkey (or Redis) | OpenBao |
|---|---|---|
| Built for | Fast, frequently changing data | Small, sensitive values: credentials and keys |
| Adding a message | Appends one item | No append: the whole conversation is read and rewritten on every turn |
| Old copies | None | Keeps the last 10 versions of every entry by default |
| "Forget this user" | Deleted at once | A normal delete is a soft delete; old versions stay readable until destroyed |
| Expiry of idle sessions | Built in (`ttl_seconds`) | No per-entry expiry |
| Size of one entry | Up to hundreds of MB | Limited (about 1 MB with the default production storage) |
| When it restarts | Back immediately | Starts *sealed*; nothing works until it is unsealed |
| Every access | Not logged by default | Written to the audit log (by design) |

Storing conversations in OpenBao would make every chat turn slower and heavier, keep extra
copies of personal data, make deletion requests harder, and put load on the system that
guards all your credentials. The first four rows were checked against a real OpenBao 2.7
server; the others are documented OpenBao behaviour.

## Credentials

```python
from sidereon_adk import Agent, OpenBao, OpenBaoSecrets, use_secrets

use_secrets(OpenBaoSecrets(OpenBao(), paths=["sidereon"]))
agent = Agent(model="openai:gpt-4o-mini")  # OPENAI_API_KEY is read from secret/sidereon
```

After `use_secrets(...)`, every part of the library that needs a credential — models,
embedders, the moderation guard, mem0, Pinecone, Astra DB — asks the secret store first.
Names are the usual variable names (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`...). Store them
as keys of a key/value secret:

```bash
bao kv put secret/sidereon OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-...
```

| Option | Meaning |
|---|---|
| `paths=["shared", "team-a"]` | Read several secrets; later ones win |
| `mount="secret"` | Where the key/value (version 2) engine is mounted |
| `cache_seconds=300` | How long values are reused; `refresh()` forces a re-read after rotation |
| `use_secrets(..., fallback_to_environment=False)` | Make OpenBao the only source (recommended in production) |

Values passed directly (`OpenAI(api_key=...)`) always win.

## Encryption at rest

```python
from sidereon_adk import OpenBaoTransit, RedisCheckpoints, RedisMemory

transit = OpenBaoTransit(key="sidereon-data")
memory = RedisMemory("redis://valkey:6379/0", encryptor=transit)
checkpoints = RedisCheckpoints("redis://valkey:6379/0", encryptor=transit)
```

`FileCheckpoints(..., encryptor=transit)` works the same way. Messages are encrypted in
batches, one request per save. The key stays inside OpenBao, can be rotated there
(`bao write -f transit/keys/sidereon-data/rotate`), and old data still decrypts.

## Logging in

`OpenBao()` reads its settings from environment variables:

| Variable | Meaning |
|---|---|
| `BAO_ADDR` | Server address, e.g. `https://bao.internal:8200` |
| `BAO_ROLE_ID`, `BAO_SECRET_ID` | **AppRole** login — recommended for services |
| `BAO_TOKEN` | A token (development, or tokens injected by an agent sidecar) |
| `BAO_NAMESPACE` | Namespace, if you use them |

On Kubernetes, use the pod's identity instead: `OpenBao(kubernetes_role="sidereon-app")`.
Tokens that expire are renewed automatically by logging in again. If OpenBao cannot be
reached or refuses access, a `ConfigError` explains what went wrong — the app does not start
with missing credentials.

## Setting up OpenBao

`deploy/openbao/setup.sh` prepares a server: it enables key/value secrets and transit
encryption, creates the `sidereon-data` key, installs the least-privilege policy
`deploy/openbao/sidereon-app.hcl` (read its own secret, encrypt and decrypt its own data,
nothing else), creates an AppRole, stores any API keys set in your shell, and prints the
app's `BAO_ROLE_ID` / `BAO_SECRET_ID`. It is safe to run again.

```bash
docker compose -f deploy/docker-compose.yml up openbao valkey     # development servers
BAO_ADDR=http://localhost:8200 BAO_TOKEN=dev-root OPENAI_API_KEY=sk-... \
  ./deploy/openbao/setup.sh > .bao.env
```

For production, run OpenBao with persistent (Raft) storage, TLS, an unseal process
(auto-unseal with a cloud KMS or HSM), audit logging, and short-lived secret ids.

## Your own secrets manager

Extend `SecretStore` (one method, `get(name)`) for another manager, or `Encryptor`
(`encrypt` and `decrypt`, both batch) for another encryption service.
