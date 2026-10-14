# Models

Every model is used the same way. Pick one with a `"provider:model"` string or an object.

```python
Agent(model="anthropic:claude-sonnet-5-5")
Agent(model=OpenAI("gpt-4o-mini", temperature=0.2, max_tokens=800))
```

## Providers

| Provider | String prefix | API key variable | Class |
| --- | --- | --- | --- |
| OpenAI | `openai:` | `OPENAI_API_KEY` | `OpenAI` |
| Anthropic | `anthropic:` | `ANTHROPIC_API_KEY` | `Anthropic` |
| Google Gemini | `gemini:` / `google:` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `Gemini` |
| Azure OpenAI | `azure:` (deployment name) | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` | `AzureOpenAI` |
| Groq | `groq:` | `GROQ_API_KEY` | |
| Mistral | `mistral:` | `MISTRAL_API_KEY` | |
| DeepSeek | `deepseek:` | `DEEPSEEK_API_KEY` | |
| Together | `together:` | `TOGETHER_API_KEY` | |
| OpenRouter | `openrouter:` | `OPENROUTER_API_KEY` | |
| Fireworks | `fireworks:` | `FIREWORKS_API_KEY` | |
| NVIDIA | `nvidia:` | `NVIDIA_API_KEY` | |
| Cerebras | `cerebras:` | `CEREBRAS_API_KEY` | |
| SambaNova | `sambanova:` | `SAMBANOVA_API_KEY` | |
| xAI | `xai:` | `XAI_API_KEY` | |
| Perplexity | `perplexity:` | `PERPLEXITY_API_KEY` | |

If you leave out the provider, common names are recognised: `gpt-4o`, `o3-mini` → OpenAI,
`claude-...` → Anthropic, `gemini-...` → Gemini.

## Local models

| Server | String prefix | Default address (override with `<PREFIX>_BASE_URL`) |
| --- | --- | --- |
| Ollama | `ollama:` | `http://localhost:11434/v1` |
| vLLM | `vllm:` | `http://localhost:8000/v1` |
| LM Studio | `lmstudio:` | `http://localhost:1234/v1` |
| llama.cpp server | `llamacpp:` | `http://localhost:8080/v1` |
| Anything else | `local:` | `LOCAL_BASE_URL` (key: `LOCAL_MODEL_API_KEY`) |

Or point at any OpenAI-style server directly (TGI, an internal gateway, a fine-tune):

```python
OpenAICompatible("my-finetune", base_url="http://gpu-box:8000/v1", api_key="internal")
```

## Settings every model accepts

`api_key`, `base_url`, `temperature`, `max_tokens`, `timeout` (seconds, default 120),
`max_retries` (default 2, for busy/temporary errors), `headers`, `http_client`, plus any
provider-specific field, which is sent as-is (for example `top_p=0.9` or `seed=7`).

```python
load_model("groq:llama-3.3-70b-versatile", temperature=0, max_tokens=300)
```

## Your own model

Wrap a function. It receives the messages and tool descriptions and returns text, a
`Message`, or a `ModelReply`; it can be sync or async.

```python
from sidereon_adk import CustomModel


def call_inhouse(messages, tools):
    return inhouse_client.complete(prompt=messages[-1].content)


agent = Agent(model=CustomModel(call_inhouse, name="inhouse-v2"))
```

For full control (streaming, tool calls, token counts) subclass `Model`:

```python
from sidereon_adk.models import Model, ModelReply


class MyModel(Model):
    provider = "acme"

    def __init__(self, name):
        self.name = name

    async def generate(self, messages, tools=None) -> ModelReply: ...

    async def stream(self, messages):  # optional
        ...
```

Make it selectable by name:

```python
from sidereon_adk.models import register_provider

register_provider("acme", lambda name, **options: MyModel(name))
Agent(model="acme:large-v3")
```

## Images

Pass image URLs or `data:` URLs with `images=[...]`. `file_to_data_url(path)` converts a
local file. Supported for OpenAI-style, Anthropic and Gemini models.
