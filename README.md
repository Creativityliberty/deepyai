# 🚀 Deepy AI - Complete AI Assistant

> Advanced RAG assistant with PDF processing, structured outputs, code execution, URL analysis, and file search powered by Gemini 2.0

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-000000?logo=next.js)](https://nextjs.org/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-4285F4?logo=google)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Latest-FF6F00)](https://www.trychroma.com/)

## ✨ Features

### Core Capabilities
- 🤖 **RAG Chat** - Intelligent chat with 3,586 indexed design patterns
- 📄 **PDF Processing** - Native PDF understanding with Gemini vision (up to 1000 pages)
- 🔍 **Structured Outputs** - Extract data into validated JSON schemas
- 💻 **Code Execution** - Generate and run Python code with 40+ libraries
- 🌐 **URL Context** - Analyze web content from up to 20 URLs
- 📁 **File Search** - Semantic search with persistent file stores

### Technical Highlights
- ⚡ **Optimized Ingestion** - Batch processing with 3000-char chunks
- 🎯 **Local Embeddings** - ChromaDB default (no API calls for embeddings)
- 🔒 **Type-Safe** - Pydantic validation throughout
- 📊 **12 API Endpoints** - Complete REST API with Swagger docs
- 🎨 **Modern UI** - Beautiful dark mode interface with Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Frontend (Next.js + Tailwind)     │
│  - Modern UI with Material Icons   │
│  - Real-time chat interface         │
└──────────────┬──────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (Port 8000)        │
│  ├─ /chat - RAG chat                │
│  ├─ /analyze-pdf - PDF analysis     │
│  ├─ /extract-structured - Extract   │
│  ├─ /execute-code - Code execution  │
│  ├─ /analyze-urls - URL analysis    │
│  └─ /file-search/* - File search    │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌─────────────┐ ┌─────────────┐
│  ChromaDB   │ │  Gemini API │
│  (Local)    │ │  (Cloud)    │
└─────────────┘ └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Gemini API Key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Creativityliberty/deepyai.git
cd deepyai
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

4. **Frontend Setup**
```bash
cd ../frontend
npm install
```

5. **Start Servers**
```bash
# Terminal 1 - Backend
cd backend
./venv/bin/python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

6. **Access the App**
- Frontend: http://localhost:3000/deepy-complete.html
- API Docs: http://localhost:8000/docs

## 📚 API Endpoints

### RAG & Chat
- `POST /chat` - Chat with RAG
- `GET /ingest` - Trigger file ingestion
- `POST /ingest-files` - Upload files for indexing

### PDF Processing
- `POST /analyze-pdf` - Analyze PDF documents

### Structured Outputs
- `POST /extract-structured` - Extract structured data
- `GET /schemas` - List available schemas

### Code Execution
- `POST /execute-code` - Execute Python code

### URL Analysis
- `POST /analyze-urls` - Analyze web URLs

### File Search
- `POST /file-search/stores` - Create file search store
- `POST /file-search/upload` - Upload to store
- `POST /file-search/query` - Query store
- `GET /file-search/stores` - List all stores

## 🎯 Usage Examples

### Code Execution
```bash
curl -X POST http://localhost:8000/execute-code \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Calculate the sum of first 20 prime numbers"}'
```

### URL Analysis
```bash
curl -X POST http://localhost:8000/analyze-urls \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Compare these sites", "urls":["https://github.com", "https://gitlab.com"]}'
```

### Structured Output
```bash
curl -X POST http://localhost:8000/extract-structured \
  -H "Content-Type: application/json" \
  -d '{"text":"Recipe text here...", "schema_type":"recipe"}'
```

## 🛠️ Tech Stack

**Backend**
- FastAPI - Modern Python web framework
- ChromaDB - Vector database for embeddings
- Google GenAI SDK - Gemini API integration
- Pydantic - Data validation

**Frontend**
- Next.js 16 - React framework
- Tailwind CSS - Utility-first CSS
- Material Symbols - Icon library
- Marked.js - Markdown rendering

**AI/ML**
- Gemini 2.0 Flash Exp - Generation model
- ChromaDB Default Embeddings - Local embeddings
- Batch Processing - Optimized ingestion

## 📊 Performance

- **Ingestion**: ~13 seconds per chunk
- **Chat Response**: ~2 seconds average
- **Code Execution**: ~3-5 seconds
- **URL Analysis**: ~2-4 seconds
- **Total Indexed**: 3,586 chunks

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
DATABASE_PATH=./deepy_db  # ChromaDB storage path
```

### Supported File Types
- **Code**: .py, .js, .ts, .java, .cpp, .c, .h
- **Documents**: .txt, .md, .pdf
- **Data**: .json, .csv, .xml

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project for your own purposes.

## 🙏 Acknowledgments

- Google Gemini API for powerful AI capabilities
- ChromaDB for efficient vector storage
- FastAPI for excellent API framework
- Next.js for modern frontend development

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Gemini 2.0**
