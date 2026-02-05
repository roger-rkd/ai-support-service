---
title: AI Support Service
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
license: mit
tags:
  - rag
  - fastapi
  - groq
  - faiss
  - llm
  - support
  - chatbot
---

# AI Support Service with RAG Pipeline

A production-ready FastAPI backend powered by Retrieval Augmented Generation (RAG) for intelligent support queries.

**🚀 Live Demo**: [https://huggingface.co/spaces/dubey-codes/ai-support-service](https://huggingface.co/spaces/dubey-codes/ai-support-service)

## Features

- **RAG Pipeline**: Retrieves relevant documents and generates contextual answers
- **Vector Search**: FAISS-powered semantic search for document retrieval
- **LLM Integration**: Groq API for fast, accurate answer generation
- **Embeddings**: Sentence Transformers for high-quality text embeddings
- **Production-Ready**: Logging, error handling, CORS, and auto-documentation

## Project Structure

```
ai-support-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   └── rag/
│       ├── __init__.py
│       ├── embedder.py      # Document & query embedding
│       ├── retriever.py     # FAISS vector search
│       └── pipeline.py      # RAG orchestration
├── data/                    # Knowledge base documents (.txt files)
│   ├── faq_password.txt
│   ├── faq_account.txt
│   ├── faq_billing.txt
│   └── faq_technical.txt
├── venv/                    # Virtual environment
├── requirements.txt
├── .env                     # Environment variables (create from .env.example)
└── .env.example
```

## Setup Instructions

### 1. Prerequisites

- Python 3.12 (recommended)
- Git
- Groq API key (get from [console.groq.com](https://console.groq.com/keys))

### 2. Installation

```bash
# Create virtual environment with Python 3.12
py -3.12 -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file:

```bash
copy .env.example .env
```

Edit `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /ask - Ask a Question

```json
{
  "question": "How do I reset my password?"
}
```

Response:
```json
{
  "answer": "To reset your password, follow these steps: 1. Go to the login page..."
}
```

### GET /health - Health Check

```json
{
  "status": "ok"
}
```

## How It Works

1. **Document Loading**: All `.txt` files in `data/` are loaded
2. **Embedding**: Documents → vector embeddings (`all-MiniLM-L6-v2`)
3. **Indexing**: Embeddings stored in FAISS index
4. **Query**: Question → embedding → retrieve top-3 docs → Groq LLM → answer

## Technologies

- **FastAPI** - Modern web framework
- **Sentence Transformers** - Text embeddings
- **FAISS** - Vector similarity search
- **Groq** - Fast LLM inference
- **Pydantic** - Data validation

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Build and Run with Docker

```bash
# Build the image
docker build -t ai-support-service .

# Run the container
docker run -d \
  --name ai-support-service \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_groq_api_key \
  -v $(pwd)/data:/app/data \
  ai-support-service

# View logs
docker logs -f ai-support-service

# Stop the container
docker stop ai-support-service
docker rm ai-support-service
```

### Docker Image Features

- **Small size**: Based on `python:3.11-slim`
- **Security**: Runs as non-root user
- **Health checks**: Automatic health monitoring
- **Production-ready**: Optimized for performance
- **Layer caching**: Fast rebuilds during development

### Environment Variables

Pass environment variables when running the container:

```bash
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
  ai-support-service
```

Or use a `.env` file with docker-compose (recommended).

## Production Deployment

### Cloud Deployment Options

**AWS ECS/Fargate:**
```bash
# Tag and push to ECR
docker tag ai-support-service:latest <aws_account_id>.dkr.ecr.region.amazonaws.com/ai-support-service:latest
docker push <aws_account_id>.dkr.ecr.region.amazonaws.com/ai-support-service:latest
```

**Google Cloud Run:**
```bash
gcloud run deploy ai-support-service \
  --image ai-support-service:latest \
  --platform managed \
  --set-env-vars GROQ_API_KEY=your_key
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name ai-support-service \
  --image ai-support-service:latest \
  --environment-variables GROQ_API_KEY=your_key
```

### Kubernetes Deployment

Create a `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-support-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-support-service
  template:
    metadata:
      labels:
        app: ai-support-service
    spec:
      containers:
      - name: ai-support-service
        image: ai-support-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: groq-secret
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 40
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: ai-support-service
spec:
  selector:
    app: ai-support-service
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f deployment.yaml
```
