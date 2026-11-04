# RAG_1 — Python Environment & JupyterLab

Python development environment for the RAG project, using a virtual environment and JupyterLab.

## 1. Project Structure

```text
RAG_1/
│
├── docs/
│   └── tools_rag.pdf
│
├── venv/
│
├── .env
│
├── requirements.txt
│
├── Untitled.ipynb
│
└── README.md
```

## 2. Requirements

- Python 3.10 or newer
- pip

## 3. Navigate to the Project Directory

```bash
cd RAG_1
```

## 4. Create the Virtual Environment

```bash
python -m venv venv
```

## 5. Activate the Virtual Environment

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

## 6. Upgrade pip

```bash
python -m pip install --upgrade pip
```

## 7. Install Dependencies

Install all packages listed in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

## 8. Start JupyterLab

```bash
python -m jupyterlab
```

JupyterLab will start locally. Open the URL displayed in the terminal in your browser.

## 9. Deactivate the Virtual Environment

When finished:

```bash
deactivate
```

---

## Quick Start

For subsequent sessions, execute:

```bash
# Navigate to the project
cd RAG_1

# Activate virtual environment
source venv/bin/activate

# Start JupyterLab
python -m jupyterlab
```

## Technologies

| Technology | Purpose |
|---|---|
| Python | Programming language |
| venv | Virtual environment |
| pip | Dependency management |
| JupyterLab | Interactive development |
| LangChain | LLM application framework |
| Ollama | Local LLM execution |
| ChromaDB | Vector database |
