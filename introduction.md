# Introduction to llm-benchmarking-py

## Project Overview

**llm-benchmarking-py** is a small toolkit of Python utilities and examples designed to benchmark and compare common algorithmic tasks for LLM-related projects. The repository provides a comprehensive collection of simple algorithms (sorting, primes), control-flow patterns (single and double loops), data-structure helpers, string utilities, and basic SQL query examples, all invoked from a single `main` entry point.

In addition to the core benchmarking toolkit, the repository includes several standalone utilities:
- A YouTube playlist downloader with both CLI and GUI interfaces
- An experimental Taipy-based chat demo for interactive AI conversations
- Example JavaScript calculator implementation

**Key Information:**
- **Package name**: `llm_benchmark`
- **Entry point**: `main:main` (via Poetry script)
- **License**: MIT

## Key Features

The project is organized into several functional areas:

**Core Benchmarking Modules:**
- **Algorithms** (`llm_benchmark.algorithms`) - Common algorithmic operations including sorting and prime number calculations
- **Control Flow** (`llm_benchmark.control`) - Single and double loop patterns for performance comparison
- **Data Structures** (`llm_benchmark.datastructures`) - Helper utilities for working with common data structures
- **Strings** (`llm_benchmark.strings`) - String manipulation and processing utilities
- **SQL** (`llm_benchmark.sql`) - Basic SQL query examples and utilities

**Standalone Utilities:**
- **YouTube Playlist Downloader (CLI)** - Command-line tool for downloading YouTube playlists using yt-dlp
- **YouTube Playlist Downloader (GUI)** - User-friendly graphical interface built with customtkinter
- **Taipy Chat Demo** - Experimental chat interface powered by OpenAI's API
- **JavaScript Calculator** - Standalone calculator implementation for HTML pages

## Technology Stack

**Core Requirements:**
- **Python 3.8+** - The minimum Python version required
- **Poetry** - Recommended package manager for dependency management and virtual environments ([installation guide](https://python-poetry.org/docs/#installation))

**Optional Dependencies** (for specific utilities):
- **yt-dlp** - Required for YouTube downloader utilities
- **customtkinter** - Required for the GUI YouTube downloader
- **taipy** - Required for the Taipy chat demo
- **openai** - Required for OpenAI API integration in the chat demo
- **python-dotenv** - For managing environment variables securely

The project can be installed either with Poetry (recommended) or using traditional pip and virtual environments.

## Getting Started

To get started with llm-benchmarking-py, follow these quick steps:

**1. Clone the repository:**
```bash
git clone <this-repo-url>
cd <repo>
```

**2. Install dependencies with Poetry (recommended):**
```bash
poetry install
```

Alternatively, you can use pip with a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
```

**3. Run the core demo:**
```bash
poetry run main
```

This executes the `main:main` entry point, which exercises functions from the `llm_benchmark` package including algorithms, data structures, SQL utilities, and more.

**Testing the project:**
```bash
# Run all tests quietly
poetry run pytest -q

# Run tests, skipping benchmarks
poetry run pytest --benchmark-skip

# Run only benchmark tests
poetry run pytest --benchmark-only tests/
```

## Learn More

For comprehensive documentation including:
- Detailed installation instructions
- Complete utility usage guides (YouTube downloaders, Taipy chat demo)
- Project architecture and structure
- Contributing guidelines
- Advanced testing and benchmarking options

Please refer to the [README.md](README.md) file in the project root.

**Contributing**: Contributions are welcome! See CONTRIBUTING.md for guidelines on development, testing, benchmarking, and submitting pull requests.

**License**: This project is licensed under the MIT License. See the license declaration in `pyproject.toml` for details.
