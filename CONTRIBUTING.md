# Contributing

## Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test class
pytest tests/test_api.py::TestDeduplication -v
```

## Adding a New Business Rule

1. Add the validation logic in `src/validators/business_rules.py`
2. Add tests in `tests/test_validators.py`
3. If configurable, add the rule to the appropriate YAML in `config/`
4. Update `docs/configuration.md`

## Commit Convention

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code restructuring
- `config:` Configuration changes
