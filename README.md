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

# 🤖 AI Support Service with RAG Pipeline

> **An intelligent AI chatbot that answers customer support questions by learning from your company's FAQ documents**

Transform your customer support with an AI assistant that reads your documentation (PDF & TXT files) and provides instant, accurate answers 24/7.

**🚀 Live Demo**: [https://huggingface.co/spaces/dubey-codes/ai-support-service](https://huggingface.co/spaces/dubey-codes/ai-support-service)

**👨‍💻 Author**: Made with ❤️ by **Rohit Kumar Dubey**
**📦 Repository**: [GitHub](https://github.com/roger-rkd/ai-support-service)

---

## ✨ Features

### Core Capabilities
- **📄 PDF & TXT Support**: Upload your FAQ documents in PDF or text format
- **🤖 Smart AI Responses**: Powered by Groq's Llama 3.3 70B model for fast, accurate answers
- **🔍 Semantic Search**: FAISS vector search understands meaning, not just keywords
- **💬 Interactive Chat UI**: Beautiful, user-friendly web interface
- **📊 Real-time Metrics**: Monitor performance with Prometheus metrics
- **🚀 Production-Ready**: Docker support, Kubernetes manifests, health checks

### Technical Features
- **RAG Pipeline**: Retrieval Augmented Generation for contextual responses
- **Vector Embeddings**: Sentence Transformers for high-quality text understanding
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Observability**: Prometheus metrics, request tracking, latency monitoring
- **CORS Enabled**: Ready for frontend integration

## 📁 Project Structure

```
ai-support-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── static/              # Frontend files
│   │   └── index.html       # Interactive chat UI
│   ├── rag/                 # RAG pipeline components
│   │   ├── __init__.py
│   │   ├── embedder.py      # Document & query embedding
│   │   ├── retriever.py     # FAISS vector search (PDF + TXT)
│   │   └── pipeline.py      # RAG orchestration
│   └── observability/       # Prometheus metrics
│       ├── __init__.py
│       └── metrics.py
├── data/                    # 📄 Add your FAQ files here (.txt or .pdf)
│   ├── faq_password.txt
│   ├── faq_account.txt
│   ├── faq_billing.txt
│   ├── faq_technical.txt
│   └── company_policies.pdf # 👈 PDF files supported!
├── k8s/                     # Kubernetes deployment manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── secret.yaml.template
├── observability/           # Monitoring stack
│   ├── docker-compose.yml   # Prometheus + Grafana
│   └── grafana-dashboard.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
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

The service will be available at:
- **💬 Interactive Chat**: http://localhost:8000
- **📖 API Docs**: http://localhost:8000/docs
- **📊 Metrics**: http://localhost:8000/metrics
- **🏥 Health Check**: http://localhost:8000/health

---

## 📄 Adding Your FAQ Documents

### Supported Formats
- **Text Files** (`.txt`): Plain text FAQs
- **PDF Files** (`.pdf`): **NEW!** Upload your PDF documentation

### How to Add Documents

1. **Place files in the `/data` folder**:
   ```bash
   data/
   ├── faq_password.txt
   ├── faq_billing.txt
   ├── company_policies.pdf    # 👈 PDF support!
   └── user_guide.pdf           # 👈 PDF support!
   ```

2. **Rebuild the index** (automatic on restart):
   ```bash
   # Restart the application
   uvicorn app.main:app --reload
   ```

3. **Or rebuild manually via Python**:
   ```python
   from app.rag.pipeline import rebuild_index
   rebuild_index()
   ```

### Document Tips
- ✅ **Use clear, well-formatted documents**
- ✅ **One topic per file recommended** (e.g., `billing.pdf`, `passwords.txt`)
- ✅ **PDFs with searchable text work best** (not scanned images)
- ✅ **Keep documents focused and concise**

---

## 💬 Using the Chat Interface

1. Open http://localhost:8000 in your browser
2. Try the example questions or type your own
3. Get instant AI-powered answers based on your FAQ documents

**Example Questions:**
- "How do I reset my password?"
- "What are your billing policies?"
- "How can I update my account information?"
- "What are your support hours?"

---

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

## 🔧 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load Documents (PDF/TXT) → Parse & Extract Text         │
├─────────────────────────────────────────────────────────────┤
│ 2. Generate Embeddings → Convert text to vectors           │
├─────────────────────────────────────────────────────────────┤
│ 3. Store in FAISS Index → Fast similarity search           │
├─────────────────────────────────────────────────────────────┤
│ 4. User Asks Question → Convert to vector                  │
├─────────────────────────────────────────────────────────────┤
│ 5. Search Similar Docs → Retrieve top-3 matches            │
├─────────────────────────────────────────────────────────────┤
│ 6. Generate Answer → Groq AI with context                  │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Process

1. **📄 Document Loading**: All `.txt` and `.pdf` files in `data/` are loaded and parsed
2. **🧮 Embedding**: Documents converted to vector embeddings using `all-MiniLM-L6-v2`
3. **💾 Indexing**: Embeddings stored in FAISS index for fast retrieval
4. **❓ Query**: User question → embedding → retrieve top-3 relevant docs
5. **🤖 Generation**: Groq's Llama 3.3 70B generates answer using retrieved context

## 🛠️ Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | High-performance REST API |
| **AI Model** | Groq (Llama 3.3 70B) | Fast LLM inference |
| **Embeddings** | Sentence Transformers | Text-to-vector conversion |
| **Vector DB** | FAISS | Similarity search |
| **PDF Parser** | PyPDF | Extract text from PDFs |
| **Metrics** | Prometheus | Observability |
| **Validation** | Pydantic | Request/response models |

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
