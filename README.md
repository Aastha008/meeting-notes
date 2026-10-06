<div align="center">

# Meeting Notes

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![CI Status](https://github.com/daily-project-factory/meeting-notes/actions/workflows/ci.yml/badge.svg)](https://github.com/daily-project-factory/meeting-notes/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated audio transcription and summarization service that converts raw meeting recordings into structured action items, discussion points, and searchable transcripts. It leverages local language models and vector embeddings to allow teams to query past conversations and extract critical project decisions effortlessly.

</div>

---

## 📋 Table of Contents

1. [Problem Statement & Target Audience](#-problem-statement--target-audience)
2. [Key Features](#-key-features)
3. [Architecture & System Design](#-architecture--system-design)
4. [Technology Stack](#-technology-stack)
5. [Installation & Virtual Environment Setup](#-installation--virtual-environment-setup)
6. [Environment Variables Configuration](#-environment-variables-configuration)
7. [Usage: CLI & API Endpoints](#-usage-cli--api-endpoints)
8. [Automated Testing Instructions](#-automated-testing-instructions)
9. [Project Structure Tree](#-project-structure-tree)
10. [Roadmap & Future Enhancements](#-roadmap--future-enhancements)
11. [License](#-license)

---

## 🎯 Problem Statement & Target Audience

### The Problem
Engineering and product teams spend countless hours in meetings, yet critical decisions, action items, and technical context are frequently lost or buried in messy personal notes and unindexed audio recordings. Manual meeting documentation is slow, inconsistent, and rarely searchable across historical project epochs.

### Target Audience
* **Engineering Managers & Tech Leads:** Seeking automated documentation of architectural decisions and engineering syncs.
* **Product Managers:** Needing instantaneous extraction of user feedback, blockers, and assigned sprint action items.
* **Remote & Distributed Teams:** Requiring asynchronous access to searchable meeting archives and semantic knowledge retrieval.

---

## ✨ Key Features

* **Automated Audio Ingestion & Transcription:** Ingests raw audio file uploads (`.mp3`, `.wav`, `.m4a`) and transcribes speech using Whisper with automatic speaker diarization.
* **Structured Intelligence Extraction:** Processes transcripts through rigorous LLM prompts via LangChain to extract key decisions, risks, and assigned action items.
* **Semantic Vector Search:** Integrates ChromaDB vector embeddings to allow teams to query past conversations using natural language.
* **High-Performance API Backend:** Exposes a robust FastAPI backend with asynchronous endpoints for managing meeting archives and querying transcripts.
* **Strict Payload Validation:** Validates all generated summaries, database payloads, and request schemas using advanced Pydantic data models.

---

## 🏗️ Architecture & System Design

The application follows a modular, separation-of-concerns design pattern dividing the codebase across domain modeling, core orchestration, API transport, and runtime execution.

```
                  +-----------------------+
                  |  Client / HTTP Calls  |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  |     src/api.py        | (FastAPI Routing & Endpoints)
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  |     src/core.py       | (Whisper, LangChain, ChromaDB)
                  +-----------+-----------+
                     |                  |
                     v                  v
         +-------------------+  +---------------+
         |   src/models.py   |  |   ChromaDB    |
         | (Pydantic Schemas)|  | Vector Store  |
         +-------------------+  +---------------+
```

### Core Architecture Modules

| Module Path | Primary Purpose |
| :--- | :--- |
| `src/models.py` | Contains Pydantic domain schemas and request/response models for meeting transcription, summaries, action items, and semantic queries. |
| `src/core.py` | Encapsulates core business logic orchestrating audio transcription, structured prompt parsing, and vector embedding retrieval. |
| `src/api.py` | Defines FastAPI HTTP routes, file upload endpoints, meeting archives management, and semantic querying endpoints. |
| `src/main.py` | Acts as the application server entrypoint and Uvicorn configuration runner. |

---

## 💻 Technology Stack

* **Language:** Python 3.10+
* **API Framework:** FastAPI & Uvicorn
* **AI & Orchestration:** LangChain, OpenAI/Local Whisper
* **Vector Database:** ChromaDB
* **Data Validation:** Pydantic v2
* **Testing Suite:** `pytest`, `pytest-asyncio`, `httpx`

---

## 🛠️ Installation & Virtual Environment Setup

Ensure you have **Python 3.10+** and `pip` installed on your local machine.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/daily-project-factory/meeting-notes.git
   cd meeting-notes
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On macOS / Linux:
   source venv/bin/activate
   
   # On Windows (Command Prompt):
   venv\Scripts\activate.bat
   
   # On Windows (PowerShell):
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔐 Environment Variables Configuration

Copy the template environment file and populate your local API keys and vector storage parameters.

```bash
cp .env.example .env
```

### `.env` Reference

```env
# Application Settings
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# AI / LLM Configuration
OPENAI_API_KEY=your-openai-api-key-here
WHISPER_MODEL_SIZE=base

# Vector Database Settings
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

---

## 🚀 Usage: CLI & API Endpoints

### Running the API Server
Start the development server using Uvicorn via the entrypoint module:

```bash
python src/main.py
```
* The interactive API documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)
* Alternative ReDoc documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core API Endpoints

| Method | Endpoint | Description | Request Body / Parameters |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/meetings/upload` | Uploads audio file, transcribes, and extracts summaries | `multipart/form-data` (`file: audio`) |
| `GET` | `/api/v1/meetings` | Retrieves a list of all processed meeting archives | `skip`, `limit` (Query parameters) |
| `GET` | `/api/v1/meetings/{meeting_id}` | Fetches full transcription & action items for a meeting | Path parameter `meeting_id` |
| `POST` | `/api/v1/meetings/query` | Performs semantic search across all stored transcripts | JSON: `{"query": "database migration risks"}` |

---

## 🧪 Automated Testing Instructions

The test suite is built using `pytest` and covers core business logic, transcription wrappers, and API route behaviors.

1. **Run the entire test suite:**
   ```bash
   pytest
   ```

2. **Run tests with verbose output & coverage report:**
   ```bash
   pytest -v --cov=src --cov-report=term-missing
   ```

3. **Run specific test modules:**
   ```bash
   pytest tests/test_core.py
   pytest tests/test_api.py
   ```

---

## 📁 Project Structure Tree

```
meeting-notes/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── core.py
│   ├── main.py
│   └── models.py
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_core.py
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **Local LLM Support:** Add direct integration with Ollama (Llama 3 / Mistral) for fully air-gapped, offline meeting processing.
- [ ] **Calendar Integration:** Auto-pull meeting metadata and participant lists directly from Google Calendar and Microsoft Outlook APIs.
- [ ] **Webhooks & Notifications:** Automatically dispatch extracted action items to Jira, Linear, Slack, or Notion channels.
- [ ] **Multi-language Diarization:** Expand speaker recognition and transcription support for non-English enterprise meetings.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` or choose to view the open-source terms for more information.

---
<div align="center">
Built with precision by Daily Project Factory 🚀
</div>