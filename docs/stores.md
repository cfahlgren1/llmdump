### Viewing / Querying

#### Hugging Face Datasets Store

To view and query Hugging Face Datasets, you can use the [Hugging Face Datasets Viewer](https://huggingface.co/docs/hub/en/datasets-viewer). You can [find example datasets on the Hugging Face Hub](https://huggingface.co/datasets?other=observers). From within here, you can query the dataset using SQL or using your own UI. Take a look at [the example](https://github.com/cfahlgren1/observers/blob/main/examples/stores/datasets_example.py) for more details.

![Hugging Face Datasets Viewer](https://raw.githubusercontent.com/cfahlgren1/observers/main/assets/datasets.png)

#### DuckDB Store

The default store is [DuckDB](https://duckdb.org/) and can be viewed and queried using the [DuckDB CLI](https://duckdb.org/#quickinstall). Take a look at [the example](https://github.com/cfahlgren1/observers/blob/main/examples/stores/duckdb_example.py) for more details.

```bash
> duckdb store.db
> from openai_records limit 10;
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬───┬─────────┬──────────────────────┬───────────┐
│          id          │        model         │      timestamp       │       messages       │ … │  error  │     raw_response     │ synced_at │
│       varchar        │       varchar        │      timestamp       │ struct("role" varc…  │   │ varchar │         json         │ timestamp │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼───┼─────────┼──────────────────────┼───────────┤
│ 89cb15f1-d902-4586…  │ Qwen/Qwen2.5-Coder…  │ 2024-11-19 17:12:3…  │ [{'role': user, 'c…  │ … │         │ {"id": "", "choice…  │           │
│ 415dd081-5000-4d1a…  │ Qwen/Qwen2.5-Coder…  │ 2024-11-19 17:28:5…  │ [{'role': user, 'c…  │ … │         │ {"id": "", "choice…  │           │
│ chatcmpl-926         │ llama3.1             │ 2024-11-19 17:31:5…  │ [{'role': user, 'c…  │ … │         │ {"id": "chatcmpl-9…  │           │
├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴───┴─────────┴──────────────────────┴───────────┤
│ 3 rows                                                                                                                16 columns (7 shown) │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Argilla Store

The Argilla Store allows you to sync your observations to [Argilla](https://argilla.io/). To use it, you first need to create a [free Argilla deployment on Hugging Face](https://docs.argilla.io/latest/getting_started/quickstart/). Take a look at [the example](https://github.com/ParagEkbote/observers/blob/main/examples/stores/argilla_example.py) for more details.

![Argilla Store](https://raw.githubusercontent.com/cfahlgren1/observers/main/assets/argilla.png)

#### OpenTelemetry Store

The OpenTelemetry "Store" allows you to sync your observations to any provider that supports OpenTelemetry! Examples are provided for [Honeycomb](https://honeycomb.io), but any provider that supplies OpenTelemetry compatible environment variables should Just Work®, and your queries will be executed as usual in your provider, against _trace_ data coming from Observers.