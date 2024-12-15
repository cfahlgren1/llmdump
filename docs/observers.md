## Observers

### Supported Observers

- [OpenAI](https://openai.com/) and every other LLM provider that implements the [OpenAI API message formate](https://platform.openai.com/docs/api-reference)
- [AISuite](https://github.com/andrewyng/aisuite), which is an LLM router by Andrew Ng and which maps to [a lot of LLM API providers](https://github.com/andrewyng/aisuite/tree/main/aisuite/providers) with a uniform interface.
- [Litellm](https://docs.litellm.ai/docs/), which is a library that allows you to use [a lot of different LLM APIs](https://docs.litellm.ai/docs/providers) with a uniform interface.
- [Docling](https://github.com/docling/docling), Docling parses documents and exports them to the desired format with ease and speed. This observer allows you to wrap this and push popular document formats (PDF, DOCX, PPTX, XLSX, Images, HTML, AsciiDoc & Markdown) to the different stores.

### Change OpenAI compliant LLM provider

The `wrap_openai` function allows you to wrap any OpenAI compliant LLM provider. Take a look at [the example doing this for Ollama](https://github.com/ParagEkbote/observers/blob/main/examples/observers/ollama_example.py) for more details.

## Stores

### Supported Stores

| Store | Example | Annotate | Local | Free | UI filters | SQL filters |
|-------|---------|----------|-------|------|-------------|--------------|
| [Hugging Face Datasets](https://huggingface.co/docs/huggingface_hub/en/package_reference/io-management#datasets) | [example](https://github.com/cfahlgren1/observers/blob/main/examples/stores/datasets_example.py) | ❌ | ❌ | ✅ | ✅ | ✅ |
| [DuckDB](https://duckdb.org/) | [example](https://github.com/ParagEkbote/observers/blob/main/examples/stores/duckdb_example.py) | ❌ | ✅ | ✅ | ❌ | ✅ |
| [Argilla](https://argilla.io/) | [example](https://github.com/ParagEkbote/observers/blob/main/examples/stores/argilla_example.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [OpenTelemetry](https://opentelemetry.io/) | [example](https://github.com/ParagEkbote/observers/blob/main/examples/stores/opentelemetry_example.py) | ︖* | ︖* | ︖* | ︖* | ︖* |
| [Honeycomb](https://honeycomb.io/) | [example](./examples/stores/opentelemetry_example.py) | ✅ |❌| ✅ | ✅ | ✅ |

(*) These features for the OpenTelemetry store, depend upon the provider you use.