# starter-repo2

Minimal starter Python repository with data analysis capabilities.

## Project Structure

```
starter-repo2/
├── Data/
│   └── Raw/
│       ├── customers_data.csv
│       ├── products_data.csv
│       └── sales_data.csv
├── docs/
│   ├── api.md
│   └── index.md
├── src/
│   └── starter_repo2/
│       ├── __init__.py
│       └── __main__.py
└── tests/
    └── test_hello.py
```

## Quick Start

1. Clone the repository:
```powershell
git clone https://github.com/cphelps34/starter-repo2.git
Set-Location C:\Repos\starter-repo2
```

2. Set up Python environment:
```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m pip install pytest
```

3. Run tests:
```powershell
python -m pytest -q
```

## Repository Information
- Repository is now hosted on GitHub at: https://github.com/cphelps34/starter-repo2
- Contains sample data files for analysis in the `Data/Raw` directory
- Documentation available in the `docs` directory
- Tests are located in the `tests` directory

## Development

The project is set up with:
- Python virtual environment
- pytest for testing
- Project structure following Python package conventions
- Sample data files for analysis
