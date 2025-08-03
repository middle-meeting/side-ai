# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Local development**: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Production**: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Docker Commands
- **Build image**: `docker build -t side-ai .`
- **Run container**: `docker run -d --name side-ai -p 8000:8000 -e OLLAMA_API_URL=<url> -e OLLAMA_MODEL_NAME=<model> side-ai`

### Environment Setup
- Create `.env` file with:
  - `OLLAMA_API_URL`: URL for Ollama API endpoint
  - `OLLAMA_MODEL_NAME`: Name of the model to use

## Architecture Overview

This is a FastAPI-based medical persona simulation service that creates virtual patient characters for healthcare training or simulation purposes.

### Core Components

**main.py:63-89** - The main chat endpoint that:
1. Accepts persona parameters (name, age, gender, symptoms, history, personality, disease)
2. Builds a structured prompt for the AI model
3. Sends requests to Ollama API for response generation
4. Returns formatted responses as virtual patient dialogue

**main.py:33-61** - Prompt building system that creates detailed persona instructions, ensuring the AI maintains character consistency and responds only as the simulated patient (no meta-commentary or bracketed descriptions)

### Data Models
- `Message`: Chat message structure with role and content
- `ChatRequest`: Complete persona definition with medical history and conversation messages  
- `ChatResponse`: Simple response wrapper

### External Dependencies
- **Ollama API**: External AI service for generating responses
- **FastAPI**: Web framework for REST API
- **Pydantic**: Data validation and serialization

### Deployment
- Containerized with Docker using Python 3.10-slim base
- Auto-deployed via GitHub Actions to VM on master branch pushes
- Uses GitHub Container Registry for image storage
- Runs on port 8000 with network configuration for production environment