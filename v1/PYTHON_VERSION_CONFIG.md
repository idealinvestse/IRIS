# Python Version Configuration - IRIS v6.0

## Current Status ✅

- **System Python**: 3.14.0 (Latest)
- **Required**: Python 3.10+
- **Recommended**: Python 3.12+
- **Status**: ✅ Compatible

## Configuration Files

### 1. `pyproject.toml` (NEW)

- **Purpose**: Modern Python project configuration (PEP 517/518)
- **Python Requirement**: `requires-python = ">=3.10"`
- **Supported Versions**: 3.10, 3.11, 3.12
- **Benefits**:
  - IDE auto-detection of Python version
  - Pip/Poetry can validate compatibility
  - Type checking and linting configuration included
  - Development dependencies separated

### 2. `.python-version` (NEW)

- **Purpose**: Version manager support (pyenv, asdf, direnv)
- **Version**: 3.12.0 (recommended)
- **Tools Supported**:
  - `pyenv`: `pyenv install 3.12.0`
  - `asdf`: `asdf install python 3.12.0`
  - Windsurf IDE: Auto-detection

## How to Use

### Option 1: Using pip (Recommended)

```bash
# Verify Python version
python --version

# Install dependencies
pip install -e ".[dev]"

# Run project
python main.py
```

### Option 2: Using Poetry

```bash
# Install Poetry if needed
pip install poetry

# Install dependencies
poetry install

# Run project
poetry run python main.py
```

### Option 3: Using Docker

```bash
# Docker automatically uses Python 3.12
docker-compose up
```

## Verification

```bash
# Check Python version
python --version

# Verify project compatibility
python -m py_compile main.py

# Run tests
pytest tests/ -v

# Type checking
mypy src/ --ignore-missing-imports
```

## IDE Configuration

### Windsurf/VS Code
- Automatically detects `pyproject.toml` and `.python-version`
- Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose: Python 3.12+ (or 3.14.0 on your system)

### PyCharm
- Settings → Project → Python Interpreter
- Select Python 3.12+

## Troubleshooting

### Issue: "Python 3.10+ required"
**Solution**: Update Python
```bash
# Windows (using Windows Store or python.org)
# macOS (using Homebrew)
brew install python@3.12

# Linux (Ubuntu/Debian)
sudo apt-get install python3.12
```

### Issue: "Module not found"
**Solution**: Reinstall dependencies
```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### Issue: "Wrong Python version in IDE"
**Solution**: Restart IDE and select correct interpreter
- Windsurf: `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose 3.12+ from list

## Dependencies

All dependencies in `requirements.txt` and `pyproject.toml` are compatible with Python 3.10+:
- FastAPI 0.115.0 ✅
- Pydantic 2.9.2 ✅
- SQLAlchemy 2.0.35 ✅
- Groq 0.11.0 ✅
- All others verified ✅

## Next Steps

1. ✅ Install Python 3.12+ (you have 3.14.0)
2. ✅ Create virtual environment: `python -m venv venv`
3. ✅ Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. ✅ Install: `pip install -e ".[dev]"`
5. ✅ Run: `python main.py`

---

**Last Updated**: 2025-11-06
**Python Version**: 3.14.0 ✅
**Status**: Ready to run
