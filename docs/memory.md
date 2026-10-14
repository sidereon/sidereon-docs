# Memory

There are two kinds of memory:

| Kind | Remembers | Keyed by | Classes |
| --- | --- | --- | --- |
| Conversation memory | The messages of one conversation | `session_id` | `InMemory`, `RedisMemory` |
| User memory | Lasting facts about a person, across all conversations | the `User` (tenant + id) | `LocalUserMemory`, `Mem0UserMemory` |

## Conversation memory

Used only when you pass a `session_id`.

```python
from sidereon_adk import Agent, InMemory

agent = Agent(model="openai:gpt-4o-mini", memory=InMemory(max_messages=50))
agent.run("I'm Priya", session_id="chat-1")
agent.run("What's my name?", session_id="chat-1")  # "Priya"
```

The request and the final answer are stored; intermediate tool steps are not, which keeps
the history short and clean.

## Shared memory with Redis or Valkey

```python
from sidereon_adk import RedisMemory

memory = RedisMemory(
    "redis://localhost:6379/0",  # valkey://... also works
    max_messages=50,  # keep the latest messages only
    ttl_seconds=30 * 24 * 3600,  # forget idle sessions (None = keep forever)
    prefix="myapp:session:",
)
```

Install with `pip install "sidereon-adk[redis]"`. You can also pass an existing
`redis.asyncio.Redis` client with `client=...`.

Add `encryptor=OpenBaoTransit()` so Valkey/Redis only stores ciphertext — see
[Secrets and encryption](secrets.md).

## Your own store

```python
from sidereon_adk.memory import Memory


class PostgresMemory(Memory):
    async def load(self, session_id): ...
    async def save(self, session_id, messages): ...
    async def clear(self, session_id): ...
```

## User memory (long-term)

User memory keeps what should be known about a person next time: their name, role,
preferences and constraints.

```python
from sidereon_adk import Agent, LocalUserMemory, User

agent = Agent(
    model="openai:gpt-4o-mini",
    memory=InMemory(),
    user_memory=LocalUserMemory(model="openai:gpt-4o-mini"),
)
priya = User(id="EMP102", tenant="acme")

agent.run("I lead the payments team and prefer short answers.", user=priya, session_id="monday")
agent.run("Draft a status update.", user=priya, session_id="friday")  # knows both facts
```

Before each request the most relevant facts are added to the instructions
(`user_memory_results`, default 5); after each answer the exchange is offered to the memory
to learn from. Anonymous users are skipped.

| Class | How it learns | Where facts live |
| --- | --- | --- |
| `LocalUserMemory()` | Keeps the user's own statements about themselves ("I prefer...", "my team...") | This process |
| `LocalUserMemory(model=...)` | A (small) model extracts short facts | This process |
| `Mem0UserMemory(api_key)` | mem0 decides what to keep, updates and de-duplicates | mem0 platform |
| `Mem0UserMemory(config={...})` | Same, self-hosted with your own vector database | Your infrastructure |

`Mem0UserMemory` needs `pip install "sidereon-adk[mem0]"`.

Forget a person on request (for example for data-protection requests):

```python
await user_memory.forget(User(id="EMP102", tenant="acme"))
```

Write your own by extending `UserMemory` with `recall`, `remember` and `forget`.

