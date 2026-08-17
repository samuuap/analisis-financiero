# Development Guide

How to set up, run, test, and extend `market-ai-agents`.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

This installs the package in editable mode plus the `dev` extra (pytest,
pytest-cov, ruff).

## Running

```bash
# Offline smoke test:
python -m src.main --ticker NVDA --mock

# Offline, JSON output:
python -m src.main --ticker NVDA --mock --json | python -m json.tool

# Real (needs DEEPSEEK_API_KEY):
python -m src.main --ticker NVDA
```

## Testing

```bash
pytest                                      # unit tests (offline)
pytest --cov=src --cov-report=term-missing  # with coverage
pytest -m integration                       # live tests (skip without key)
```

Integration tests are marked with `@pytest.mark.integration` and auto-skip when
`DEEPSEEK_API_KEY` is absent.

## Linting

```bash
ruff check .
ruff format --check .
```

The configured rules are `E`, `F`, `I`, `UP`, `B` with a 100-column line limit.

## Code style

- **No silent exceptions.** Every `except` logs and/or degrades; never
  `except: pass`.
- **No hardcoded keys.** All secrets come from `Settings.from_env()`.
- **Model name.** Use `deepseek-v4-flash` / `deepseek-v4-pro` only; never
  `deepseek-chat` or `deepseek-reasoner`.
- **No order execution.** This project never connects to a broker or places
  orders.

## Adding a data provider

1. Implement the relevant `Protocol` in `src/tools/protocols.py`
   (`MarketDataProvider` or `NewsProvider`).
2. Raise a domain exception (`MarketDataError` / `NewsError`) on empty or invalid
   results.
3. Register it in `src/main.py` (or pass it directly into `MarketCrew`).

Because agents depend only on the protocol, no agent code needs to change.

## Adding an indicator

Add a pure function to `src/utils/indicators.py` that operates on a pandas
Series/DataFrame, wire it into `compute_all`, and expose it on the
`TechnicalAnalysis` model. Add a unit test in `tests/unit/test_indicators.py`
with a known-value assertion.

## Adding an agent

CrewAI agents are built by small factory functions in `src/agents/`. Each agent
maps to a `Task` builder in `src/tasks/`. To add an agent:

1. Create a builder that returns a `crewai.Agent`.
2. Create a matching `Task` builder.
3. Insert both into `MarketCrew.build_crew` in the desired position of the
   sequential list.

## Release checklist

Before considering a change done, run the full verification:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
pytest -m integration          # only if a key is available
python -m src.main --help
python -m src.main --ticker NVDA --mock
python -m src.main --ticker NVDA --mock --json | python -m json.tool
```

Also verify: no secrets committed (`git grep` for a real key pattern), imports
are clean (`ruff` F401/F811), and the README's from-scratch instructions still
work.
