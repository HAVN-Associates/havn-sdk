# Contributing to HAVN Python SDK

Thank you for considering contributing to HAVN Python SDK!

## Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/havn/havn-python-sdk.git
cd havn-python-sdk
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies**

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=havn --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

## Code Style

We follow PEP 8 and use automated tools:

```bash
# Format code with black
black havn tests

# Sort imports
isort havn tests

# Check with flake8
flake8 havn tests

# Type check with mypy
mypy havn
```

## Pull Request Process

1. **Create a branch** - Use descriptive names: `feature/add-webhook`, `fix/auth-error`
2. **Write tests** - All new features must have tests
3. **Update docs** - Update README.md and examples if needed
4. **Run tests** - Ensure all tests pass
5. **Submit PR** - Provide clear description of changes

## Commit Messages

Follow conventional commits:

- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `test: Add or update tests`
- `refactor: Code refactoring`
- `chore: Maintenance tasks`

## Questions?

- 📧 Email: bagus@intelove.com
- 💬 Discussions: https://github.com/havn/havn-python-sdk/discussions
