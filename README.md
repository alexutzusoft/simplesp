# SimpleSP: Simple Sentence Predictor

SimpleSP is a minimalist, retrieval-based sentence prediction engine. It is engineered to be **lightweight**, **local-first**, and **deterministic**, providing a private and high-performance completion assistant for developers and technical writers without the complexity of large-scale language models.

![SimpleSP Status](https://img.shields.io/badge/Status-Open%20Source-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Core Features

- **Privacy-Centric**: All processing occurs locally. No data is transmitted to external servers.
- **High Performance**: Near-instant retrieval speeds, optimized for large datasets.
- **Deterministic Logic**: Utilizes advanced regex and template matching for predictable results.
- **Live Updates**: Implements hot-reloading to immediately reflect changes in the local knowledge base.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (Recommended) or `pip`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alexutzusoft/SimpleSP.git
   cd SimpleSP
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   # Alternatively, using pip:
   pip install -r requirements.txt
   ```

### Usage

1. **Populate Data**: Add your text-based source files (`.txt`, `.py`, `.json`, etc.) to the `data/` directory.
2. **Execute Application**:
   ```bash
   uv run main.py
   ```
3. **Web Interface**: Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the prediction interface.

## Configuration

SimpleSP can be configured via the `config.json` file in the project root:

```json
{
    "data_dir": "data",
    "supported_extensions": [".txt", ".py", ".json"],
    "reload_check_interval": 2
}
```

## License

This project is licensed under the MIT License. Refer to the `LICENSE` file for full details.

---
Developed by Alexutzu from the TreeSoft Team.