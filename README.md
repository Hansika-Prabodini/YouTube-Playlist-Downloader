# llm-benchmarking-py

A small toolkit of Python utilities and examples to benchmark and compare common algorithmic tasks for LLM-related projects. It includes simple algorithms (sorting, primes), control-flow patterns (single and double loops), data-structure helpers, string utilities, and basic SQL query examples invoked from a single `main` entry point. The repository also contains a couple of standalone utilities: a YouTube playlist downloader (CLI and GUI) and an experimental Taipy-based chat demo.

- Package name: `llm_benchmark`
- Entry point: `main:main` (via Poetry script)
- License: MIT

## Requirements
- Python 3.8+
- Poetry (recommended) https://python-poetry.org/docs/#installation
- Optional (for utilities):
  - `yt-dlp` for YouTube downloaders
  - `customtkinter` for the GUI YouTube downloader
  - `taipy`, `openai`, and `python-dotenv` for the Taipy chat demo

## Quick Start

### 1) Clone and set up
```bash
# clone
git clone <this-repo-url>
cd <repo>

# create/install environment
poetry install
```

If you prefer not to use Poetry, you can create a virtual environment and install extras manually:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -U pip
# Optional extras for utilities
pip install yt-dlp customtkinter taipy openai python-dotenv
```

## Build and Run
You can either build the environment with Poetry directly or via the helper script.

- Using Poetry (recommended):
```bash
poetry install
```

- Using the helper script:
```bash
chmod +x build.sh
./build.sh
```
Note: `build.sh` sources an optional `variables.sh`. If it doesn’t exist, you can ignore the warning or run `poetry install` directly.

### Run the core demo
```bash
poetry run main
```
This executes `main:main`, which exercises functions from the `llm_benchmark` package (algorithms, data structures, SQL, etc.).

## Testing and Benchmarking
- Run tests (quiet):
```bash
poetry run pytest -q
```

- Run tests skipping benchmarks:
```bash
poetry run pytest --benchmark-skip
```

- Run only benchmarks (if you have benchmark tests):
```bash
poetry run pytest --benchmark-only tests/
```

## Utilities

### YouTube Playlist Downloader (CLI)
```bash
# prerequisites
pip install yt-dlp

# run
python youtube_Download-cli.py
```

### YouTube Playlist Downloader (GUI)
```bash
pip install yt-dlp customtkinter
python youtube_downloader-gui.py
```

### Taipy Chat Demo (experimental)
```bash
pip install taipy openai python-dotenv
export OPENAI_API_KEY=your_key_here  # or set in a .env
python file-v1-main.py
```

### JavaScript Calculator Example
The `script.js` file contains a standalone calculator implementation for use in an HTML page. Include it in your HTML and ensure matching element IDs (`number1`, `number2`, `calculateBtn`, `result`).

## Project Structure
- `main.py` – calls into the `llm_benchmark` modules to demonstrate operations
- `pyproject.toml` – Poetry configuration (script entry point `main:main`)
- `build.sh` – helper to run `poetry install` (optionally sources `variables.sh`)
- `test_file_selection.py` – simple test example
- `youtube_Download-cli.py`, `youtube_downloader-gui.py` – standalone downloaders
- `file-v1-main.py` – Taipy GUI chat demo
- `script.js` – example JavaScript code

## Architecture
```mermaid
flowchart TD
    A[CLI Entry: poetry run main] -->|invokes| B[main.py]
    B --> C[llm_benchmark.algorithms]
    B --> D[llm_benchmark.control]
    B --> E[llm_benchmark.datastructures]
    B --> F[llm_benchmark.strings]
    B --> G[llm_benchmark.sql]

    subgraph Extras / Utilities
        H[YouTube CLI (yt-dlp)]
        I[YouTube GUI (tk/customtkinter + yt-dlp)]
        J[Taipy Chat Demo (OpenAI)]
        K[script.js Calculator]
    end

    A -. separate scripts .-> H
    A -. separate scripts .-> I
    A -. separate scripts .-> J
    A -. static asset .-> K
```

## Contributing
Contributions are welcome! Please see CONTRIBUTING.md for guidelines on development, testing, benchmarking, and submitting pull requests.

## License
MIT. See the license declaration in `pyproject.toml`.
