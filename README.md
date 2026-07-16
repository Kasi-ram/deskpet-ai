# DeskPet AI

DeskPet AI is a Streamlit-based airline knowledge assistant built with Python, Groq, Gemini embeddings, ChromaDB, and LangGraph. It supports document-grounded answers, calculator requests, and per-session conversation memory.

---

## Features

* Streamlit chat interface with LangGraph routing
* PDF and UTF-8 text document ingestion
* Gemini embeddings and ChromaDB retrieval
* Groq-powered evidence selection and grounded answers
* Calculator tool and per-session conversation memory
* Per-session knowledge-base isolation and reset

---

## Tech Stack

* Python 3.12+
* Streamlit
* Groq API and Google Gemini embeddings API
* LangGraph and ChromaDB
* python-dotenv
* Git & GitHub

---

## Project Structure

```text
DeskPetAI/
│
├── app.py
├── test_gemini.py
├── .env
├── requirements.txt
│
├── assets/
│   ├── css/
│   ├── images/
│   └── sounds/
│
├── components/
│
├── services/
│   └── gemini_service.py
│
├── rag/
├── agents/
├── tools/
├── prompts/
├── memory/
├── data/
└── tests/
```

---

## Prerequisites

* Python 3.12 or later
* Git
* VS Code (recommended)
* Groq API key and Google Gemini API key

---

## Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DeskPetAI
```

---

## Create a Virtual Environment

### Windows

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

---

## Create the Environment File

Create a file named:

```text
.env
```

Add the API keys used for generation and embeddings:

```text
GEMINI_API_KEY=YOUR_API_KEY
GROQ_API_KEY=YOUR_API_KEY
# Optional: GROQ_MODEL=llama-3.1-8b-instant
# Optional: RAG_MAX_DISTANCE=0.35
# Optional: MAX_UPLOAD_BYTES=20971520
```

> Do **not** commit the `.env` file to GitHub.

---

## Run regression tests

```bash
python -m unittest discover -s tests
```

---

## Run the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Common Commands

Activate virtual environment

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install a new package

```bash
python -m pip install <package-name>
```

Update requirements

```bash
python -m pip freeze > requirements.txt
```

Deactivate virtual environment

```bash
deactivate
```

---

## Environment Variables

| Variable       | Description           |
| -------------- | --------------------- |
| GEMINI_API_KEY | Google Gemini embedding API key |
| GROQ_API_KEY | Groq generation and evidence-selection API key |
| GROQ_MODEL | Optional Groq model override |
| RAG_MAX_DISTANCE | Optional maximum retrieval distance. Defaults to `0.35` for cosine collections and `1.0` for legacy L2 collections. |
| MAX_UPLOAD_BYTES | Maximum upload size in bytes (default 20 MiB) |

---

## Current Progress

* [x] Project setup
* [x] GitHub repository
* [x] Virtual environment
* [x] Streamlit UI
* [x] Google Gemini integration
* [x] LangGraph routing and streamed progress
* [x] Chat memory
* [x] PDF/text upload and embeddings
* [x] ChromaDB-backed RAG
* [x] Evidence selection and calculator tool
* [ ] Voice Assistant

---

## Learning Goals

This project is intended to explore and understand:

* Streamlit
* Prompt Engineering
* Google Gemini API
* AI Application Architecture
* Retrieval-Augmented Generation (RAG)
* Embeddings
* Vector Databases
* AI Agents
* Tool Calling
* Conversation Memory

---

## Security

Never commit:

* `.env`
* API Keys
* Tokens
* Credentials

Make sure the following entries exist in `.gitignore`:

```text
.venv/
.env
__pycache__/
*.pyc
```

---

## Future Roadmap

### Version 0.1

* Project setup
* Streamlit UI
* Gemini integration

### Version 0.2

* Chat improvements
* Streaming responses
* Better UI components

### Version 0.3

* PDF upload
* Embeddings
* ChromaDB

### Version 0.4

* Retrieval-Augmented Generation (RAG)

### Version 0.5

* AI Agent
* Tool Calling

### Version 1.0

* Complete DeskPet AI Assistant
* Voice interaction
* Memory
* Raspberry Pi deployment
