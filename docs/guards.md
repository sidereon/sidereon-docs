# Guards

Guards check the request before the model sees it, and the answer before it is returned.
They can **mask** text (the run continues with the cleaned text) or **block** the run.

```python
from sidereon_adk import Agent, KeywordGuard, PIIGuard

agent = Agent(
    model="openai:gpt-4o-mini",
    guards=[
        KeywordGuard.prompt_injection(),  # "ignore previous instructions", ...
        KeywordGuard(["salary of", "home address"]),  # off-limits topics
        PIIGuard({"EMPLOYEE_ID": r"EMP\d{6}"}, block=["CREDIT_CARD"]),
    ],
)
```

When a guard blocks, the run stops before calling the model and returns:

```python
response.blocked  # True
response.reason  # "Blocked phrase: ignore previous instructions"
response.content  # the agent's blocked_message
```

## Built-in guards

| Guard | Does | Install |
| --- | --- | --- |
| `PIIGuard(patterns, block, reversible, ...)` | Masks emails, phone numbers, card numbers, IP addresses and your own patterns | core |
| `KeywordGuard(phrases, check_outputs=False)` | Blocks text containing any phrase (case-insensitive) | core |
| `KeywordGuard.prompt_injection()` | Pre-filled with common instruction-override phrases | core |
| `PresidioGuard(entities, patterns, ...)` | Finds 30+ kinds of personal data with Microsoft Presidio: names, locations, national IDs (e.g. `IN_PAN`, `IN_AADHAAR`), IBANs... | `[presidio]` + a spaCy model |
| `LlamaFirewallGuard(scanners, output_scanners)` | Meta LlamaFirewall: Prompt Guard (injection/jailbreak), hidden characters, regex, code safety | `[llamafirewall]` |
| `ClassifierGuard(model, blocked_labels, threshold)` | Any Hugging Face text classifier, run locally; defaults to Prompt Guard | `[transformers]` |
| `ClassifierGuard.toxicity()` | Insults, threats and hate in requests and answers | `[transformers]` |
| `ModerationGuard(categories)` | OpenAI-style moderation service (hate, violence, self-harm...) | core |

Guards that call a service block when the service is unreachable (`fail_closed=True`).

### Presidio

```python
from sidereon_adk import PresidioGuard

PresidioGuard(
    ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "IN_PAN", "CREDIT_CARD"],
    patterns={"EMPLOYEE_ID": r"EMP\d{6}"},  # your own types
    block=["CREDIT_CARD"],  # stop instead of masking
    score_threshold=0.5,
    spacy_model="en_core_web_lg",  # python -m spacy download en_core_web_lg
)
```

### Reversible masking

With `reversible=True` (on `PIIGuard` and `PresidioGuard`) personal data is replaced by
placeholders such as `<PERSON_1>` and `<EMAIL_ADDRESS_1>` before the model sees it, and the
real values are put back into the final answer. The model never sees the real data, but the
user gets a normal answer.

Tools receive the placeholders. A tool that truly needs a real value can ask for it:

```python
privacy = PresidioGuard(reversible=True)


@tool
def send_email(to: str, body: str, context: RunContext) -> str:
    """Send an email."""
    return mailer.send(privacy.reveal(to, context), body)
```

## Your own guard

Override one or both checks to connect any other safety service. For personal data, extend
`MaskingGuard` and implement only `find(text)`; masking, blocking and reversible
placeholders are handled for you.

```python
from sidereon_adk import Guard, GuardResult


class Moderation(Guard):
    async def check_output(self, text, context):
        if await moderation_api.is_toxic(text):
            return GuardResult(allowed=False, text=text, reason="Toxic content")
        return GuardResult(text=text)
```

Guards run in the order given; each receives the text produced by the previous one.
