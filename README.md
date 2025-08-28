# llm-benchmarking-py

A collection of Python functions to benchmark LLM projects.

## Usage

### Build:

```shell
poetry install
```

### Run Main:

```shell
poetry run main
```

### Run Unit Tests:

```shell
poetry run pytest --benchmark-skip tests/
```

### Run Benchmarking:

```shell
poetry run pytest --benchmark-only tests/
```