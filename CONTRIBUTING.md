# Contributing to llm-benchmarking-py

Thanks for taking the time to contribute! This guide explains how to set up your environment, follow the project style, add features/benchmarks, and submit changes.

## Table of contents
- Development setup
- Branching model
- Code style and formatting
- Running tests and benchmarks
- Adding new modules/benchmarks
- Commit messages and pull requests
- Issue reporting and triage

## Development setup
1) Prerequisites
- Python 3.8+
- Poetry

2) Install dependencies
```bash
poetry install
```

3) Activate the virtual environment when needed
```bash
poetry shell
```

4) Pre-commit style helpers (optional)
If you use pre-commit, you can configure `black` and `isort` to run automatically. Otherwise, run them manually as shown below.

## Branching model
- main: Always releasable. No direct commits unless small docs/non-functional fixes.
- feature/<short-name>: New features, modules, or doc updates.
- fix/<short-name>: Bug fixes.
- chore/<short-name>: Tooling or dev-experience changes.

## Code style and formatting
- Use `black` and `isort` (already included as dev dependencies):
```bash
poetry run isort .
poetry run black .
```
- Keep functions small and focused, with clear docstrings where helpful.
- Prefer pure functions and deterministic behavior for benchmarks.

## Running tests and benchmarks
- Run tests:
```bash
poetry run pytest -q
```
- Skip benchmarks during quick test runs:
```bash
poetry run pytest --benchmark-skip
```
- Run only benchmarks (assuming benchmark tests exist in tests/):
```bash
poetry run pytest --benchmark-only tests/
```

## Adding new modules/benchmarks
When contributing to the `llm_benchmark` examples or adding new benchmark targets:
- Place new modules under an appropriate package path (e.g., `llm_benchmark/algorithms/`, `llm_benchmark/strings/`, etc.).
- Provide simple, deterministic functions that are easy to benchmark.
- Add a minimal usage example in `main.py` or a dedicated demo file.
- If adding pytest benchmarks, use `pytest-benchmark` markers and keep datasets small enough to run quickly by default.

## Commit messages and pull requests
- Write descriptive commit messages following conventional style where possible (feat:, fix:, docs:, chore:, refactor:, test:).
- Open a PR targeting `main` and include:
  - A summary of changes and rationale.
  - Notes on performance impact (for benchmark changes).
  - Screenshots or output samples when helpful.
- Keep PRs small and focused. Large refactors should be discussed first in an issue.

## Issue reporting and triage
- Use issues for bugs, feature requests, or performance regressions.
- Include steps to reproduce, expected vs actual behavior, and environment details.
- For benchmark regressions, include the benchmark output and commit baseline if available.

## Security Considerations

Security is a critical aspect of software development. When contributing code, please follow these security best practices:

### Before Committing

1. **Never commit secrets**
   - No API keys, passwords, tokens, or credentials
   - Use environment variables (`.env` files)
   - Verify `.env` is in `.gitignore`
   ```bash
   # Check for potential secrets before committing
   git diff | grep -i "api_key\|password\|secret\|token"
   ```

2. **Validate all user input**
   - URLs, file paths, and any user-provided data
   - Use allowlists for known-good values when possible
   - Implement reasonable input length limits
   - Sanitize input to remove control characters

3. **Use subprocess safely**
   ```python
   # ✅ GOOD: Use list of arguments, no shell=True
   subprocess.run(["yt-dlp", "--version"])
   
   # ❌ BAD: shell=True with user input (command injection risk)
   subprocess.run(f"yt-dlp {user_url}", shell=True)
   ```

4. **Handle errors securely**
   - Don't leak sensitive information in error messages
   - Log errors appropriately (avoid logging secrets)
   - Provide user-friendly error messages

5. **Run security checks**
   ```bash
   # Install security tools
   poetry add --group dev safety bandit
   
   # Run checks before committing
   poetry run safety check          # Check for vulnerable dependencies
   poetry run bandit -r . -ll       # Security linting
   ```

### Security Review Checklist

Before submitting a pull request, ensure:

- [ ] No hardcoded secrets, API keys, or passwords
- [ ] All user input is validated and sanitized
- [ ] Subprocess calls use argument lists (not shell=True)
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are up to date (`poetry update`)
- [ ] Security checks pass (`safety check` and `bandit`)
- [ ] New code includes appropriate input validation
- [ ] Authentication/authorization is properly implemented (if applicable)

### Security Resources

- [SECURITY.md](SECURITY.md) - Security policy and reporting vulnerabilities
- [SECURITY_RECOMMENDATIONS.md](SECURITY_RECOMMENDATIONS.md) - Detailed security guidance
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Implementation checklist

## Code of Conduct
By participating, you agree to abide by a standard open-source code of conduct. Be respectful and constructive in all discussions.
