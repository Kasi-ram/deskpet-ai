# DeskPet AI

DeskPet AI is a retro-themed AI desktop assistant built with **Python**, **Streamlit**, and **Google Gemini**. This project is designed as a learning journey covering modern AI concepts such as LLM integration, Retrieval-Augmented Generation (RAG), AI Agents, Memory, and Tool Calling.

---

## Features

* Retro airport terminal UI
* Chat interface built with Streamlit
* Google Gemini integration
* Modular architecture
* Ready for RAG integration
* Extensible design for AI Agents and Tools

---

## Tech Stack

* Python 3.12+
* Streamlit
* Google Gemini API
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
* Google Gemini API Key

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

Add your Gemini API key:

```text
GEMINI_API_KEY=YOUR_API_KEY
```

> Do **not** commit the `.env` file to GitHub.

---

## Run the Gemini Test

Verify that Gemini is configured correctly.

```bash
python test_gemini.py
```

Expected output:

```text
Hello! How can I help you today?
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
| GEMINI_API_KEY | Google Gemini API Key |

---

## Current Progress

* [x] Project setup
* [x] GitHub repository
* [x] Virtual environment
* [x] Streamlit UI
* [x] Google Gemini integration
* [ ] Streaming responses
* [ ] Chat memory
* [ ] PDF upload
* [ ] Embeddings
* [ ] ChromaDB
* [ ] RAG
* [ ] AI Agents
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
