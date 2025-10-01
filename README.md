# llm-benchmarking-py

A collection of Python functions to benchmark LLM projects.

## Usage

### Build

```shell
poetry install
```

### Run CLI demos

```shell
poetry run main
```

### Run unit tests

There is no dedicated tests/ folder in this repo snapshot. To run any discovered tests:

```shell
poetry run pytest --benchmark-skip
```

To run benchmarks only (if benchmark tests are present):

```shell
poetry run pytest --benchmark-only
```

### Run the Taipy Chat demo (optional)

This repository includes a simple Taipy-based chat UI that talks to the OpenAI API.

1. Create a .env file at the project root and add your API key:

```
OPENAI_API_KEY=your_key_here
```

2. Start the app:

```shell
poetry run python file-v1-main.py
```

The app will launch a local web UI.
