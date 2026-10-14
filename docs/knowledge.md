# Knowledge (your documents)

Give an agent access to your own content so answers are grounded in it.

```python
from sidereon_adk import Agent, Document, KeywordRetriever

docs = [
    Document(id="leave", text="Employees get 12 casual leave days a year."),
    Document(id="wfh", text="Work from home is allowed two days a week."),
]
agent = Agent(model="openai:gpt-4o-mini", knowledge=KeywordRetriever(docs), knowledge_results=3)

response = agent.run("How many leave days do I get?")
response.sources  # the documents that were used
```

The best matching passages are added to the instructions, and the model is asked to cite
their ids.

## Let the model decide when to search

```python
agent = Agent(model=..., tools=[KeywordRetriever(docs).as_tool()])
```

## Loading and splitting your files

```python
from sidereon_adk.knowledge import load_files, split_documents

documents = load_files("handbook/", "policies/leave.pdf")  # .txt .md .rst .pdf (pdf: [pdf] extra)
chunks = split_documents(documents, max_chars=1000, overlap=100)  # ids like "handbook/leave.md#3"
```

Long texts are split at paragraph and sentence ends where possible, with a small overlap so
no idea is cut in half.

## Meaning-based search

`VectorRetriever` finds passages by meaning rather than exact words. It combines an
**embedder** (turns text into numbers) with a **vector store** (keeps and searches them).

```python
from sidereon_adk import VectorRetriever
from sidereon_adk.knowledge import load_embedder
from sidereon_adk.knowledge.stores import QdrantStore

retriever = VectorRetriever(
    load_embedder("openai:text-embedding-3-small"),
    QdrantStore("handbook", url="http://localhost:6333"),
)
await retriever.add(chunks)  # embeds in batches and stores
agent = Agent(model=..., knowledge=retriever)
```

Change the database by changing one line; the rest of your code stays the same.

### Embedders

| String | Class | Runs |
| --- | --- | --- |
| `openai:<model>` | `OpenAIEmbedder` | OpenAI |
| `ollama:<model>`, `vllm:<model>` | `OpenAIEmbedder` | Your machine / server |
| `mistral:`, `jina:`, `together:`, `nvidia:` | `OpenAIEmbedder` | Those services |
| `voyage:<model>` | `VoyageEmbedder` | Voyage AI |
| `gemini:<model>` | `GeminiEmbedder` | Google |
| `cohere:<model>` | `CohereEmbedder` | Cohere |
| `local:<model>` (e.g. `local:BAAI/bge-small-en-v1.5`) | `SentenceTransformerEmbedder` | Your machine (`[local-embeddings]` extra) |
| any function | `FunctionEmbedder(fn)` | Anything |

### Vector databases

| Class | Database | Extra | Notes |
| --- | --- | --- | --- |
| `InMemoryVectorStore()` | In this process | core | Default; good up to tens of thousands of passages |
| `FAISSStore()` | FAISS | `[faiss]` | Very fast, in this process |
| `ChromaStore(collection, path=/host=)` | Chroma | `[chroma]` | Memory, local folder or server |
| `QdrantStore(collection, url=/path=)` | Qdrant | `[qdrant]` | Memory, local folder, server or cloud |
| `MilvusStore(collection, uri=)` | Milvus / Zilliz | `[milvus]` | `./milvus.db` runs locally (Milvus Lite) |
| `WeaviateStore(collection, url=)` | Weaviate | `[weaviate]` | Local or cloud |
| `PGVectorStore(dsn, table=)` | PostgreSQL + pgvector | `[pgvector]` | Table created automatically |
| `ElasticsearchStore(index, url=)` | Elasticsearch 8+ | `[elasticsearch]` | Index created automatically |
| `OpenSearchStore(index, hosts=)` | OpenSearch | `[opensearch]` | Index created automatically |
| `PineconeStore(index, namespace=)` | Pinecone | `[pinecone]` | Create the index (cosine) first |
| `MongoDBAtlasStore(uri=, index_name=)` | MongoDB Atlas | `[mongodb]` | `create_index(dimension)` once |
| `AzureAISearchStore(index, endpoint=, filter_fields=)` | Azure AI Search | `[azure-search]` | Create the index first (fields below) |
| `AstraDBStore(collection, api_endpoint=)` | DataStax Astra DB | `[astra]` | Create a vector collection first |

Every store keeps the id, text and metadata, uses cosine similarity, replaces documents
with the same id, and supports `delete(ids)`. Each also accepts an existing client
(`client=` or the collection/index object) so you can reuse your connection settings.

**Filters.** Limit a search to documents whose metadata matches:

```python
hr_only = VectorRetriever(embedder, store, filter={"department": "hr"})
```

For Azure AI Search, list the filterable keys in `filter_fields`; the index needs fields
`id` (key), `doc_id`, `text`, `metadata` (string), `embedding` (vector) plus one filterable
field per name.

## Your own search (another database or service)

```python
from sidereon_adk.knowledge import Retriever, Document


class SearchServiceRetriever(Retriever):
    async def search(self, query: str, k: int = 4) -> list[Document]:
        hits = await my_search_api.query(query, top=k)
        return [Document(id=h.id, text=h.body, score=h.score) for h in hits]
```

Or add a new database by extending `knowledge.stores.VectorStore` (`add`, `search`,
`delete`) — see [Architecture](architecture.md#add-a-vector-database).
