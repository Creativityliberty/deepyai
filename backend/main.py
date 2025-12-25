from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import os
import json
from dotenv import load_dotenv
from engine import DeepyEngine
from schemas import get_schema, SCHEMA_REGISTRY

# Load environment variables
load_dotenv()

app = FastAPI(title="Deepy AI Backend")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set")

engine = DeepyEngine(api_key=API_KEY, db_path="./deepy_db")

class ChatRequest(BaseModel):
    message: str

class Source(BaseModel):
    name: str
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = engine.chat(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingest")
async def start_ingest():
    """Trigger ingestion of data files."""
    data_dir = "../data"
    total_files = 0
    results = {}
    
    if not os.path.exists(data_dir):
        return {"status": "error", "message": f"Data directory {data_dir} not found"}
        
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_dir, filename)
            count = engine.ingest_file(file_path)
            results[filename] = count
            total_files += count
            
    return {
        "status": "success", 
        "total_documents_indexed": total_files,
        "details": results
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ingest-files")
async def ingest_files(files: List[UploadFile] = File(...)):
    """Handle file uploads from the drag-and-drop interface."""
    total_indexed = 0
    results = {}
    
    # Save uploaded files temporarily
    temp_dir = "/tmp/deepy_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    for file in files:
        try:
            # Save file temporarily
            temp_path = os.path.join(temp_dir, file.filename)
            content = await file.read()
            
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            # Ingest the file
            count = engine.ingest_file(temp_path)
            results[file.filename] = count
            total_indexed += count
            
            # Clean up
            os.remove(temp_path)
            
        except Exception as e:
            results[file.filename] = {"error": str(e)}
            
    return {
        "status": "success",
        "total_indexed": total_indexed,
        "details": results
    }


# New endpoints for PDF and Structured Outputs

class PDFAnalysisRequest(BaseModel):
    prompt: str = "Summarize this document"

class PDFAnalysisResponse(BaseModel):
    answer: str
    file_info: dict

@app.post("/analyze-pdf", response_model=PDFAnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...), prompt: str = "Summarize this document"):
    """Analyze a PDF file using Gemini's native PDF understanding."""
    try:
        # Save uploaded file temporarily
        temp_dir = "/tmp/deepy_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Write file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Process PDF
        result = engine.process_pdf(temp_path, prompt)
        
        # Clean up
        os.remove(temp_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StructuredOutputRequest(BaseModel):
    text: str
    schema_type: str  # e.g., "recipe", "invoice", "feedback", "design_pattern"
    custom_schema: Optional[dict] = None
    prompt: Optional[str] = None

class StructuredOutputResponse(BaseModel):
    data: Any
    schema_type: str

@app.post("/extract-structured")
async def extract_structured(request: StructuredOutputRequest):
    """Extract structured data from text according to a schema."""
    try:
        # Get schema
        if request.custom_schema:
            schema = request.custom_schema
        else:
            try:
                schema = get_schema(request.schema_type)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Generate structured output
        result = engine.generate_structured_output(
            text=request.text,
            schema=schema,
            prompt=request.prompt
        )
        
        # Convert Pydantic model to dict if needed
        if hasattr(result, 'model_dump'):
            data = result.model_dump()
        else:
            data = result
        
        return {
            "data": data,
            "schema_type": request.schema_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schemas")
async def list_schemas():
    """List available schema types for structured outputs."""
    return {
        "schemas": list(SCHEMA_REGISTRY.keys()),
        "details": {
            name: {
                "description": schema.__doc__ or "No description",
                "fields": list(schema.model_fields.keys()) if hasattr(schema, 'model_fields') else []
            }
            for name, schema in SCHEMA_REGISTRY.items()
        }
    }


# Advanced Gemini Tools Endpoints

class CodeExecutionRequest(BaseModel):
    prompt: str

class CodeExecutionResponse(BaseModel):
    text_parts: List[str]
    code_parts: List[dict]
    output_parts: List[dict]

@app.post("/execute-code", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code using Gemini's code execution tool."""
    try:
        result = engine.execute_code(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class URLAnalysisRequest(BaseModel):
    prompt: str
    urls: List[str]

class URLAnalysisResponse(BaseModel):
    answer: str
    url_metadata: List[dict]

@app.post("/analyze-urls", response_model=URLAnalysisResponse)
async def analyze_urls(request: URLAnalysisRequest):
    """Analyze content from URLs using Gemini's URL context tool."""
    try:
        if len(request.urls) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 URLs allowed")
        result = engine.analyze_urls(request.prompt, request.urls)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FileSearchStoreRequest(BaseModel):
    display_name: str

class FileSearchStoreResponse(BaseModel):
    store_name: str

@app.post("/file-search/stores", response_model=FileSearchStoreResponse)
async def create_file_search_store(request: FileSearchStoreRequest):
    """Create a new file search store."""
    try:
        store_name = engine.create_file_search_store(request.display_name)
        return {"store_name": store_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/file-search/upload")
async def upload_to_file_search(
    file: UploadFile = File(...),
    store_name: str = "",
    display_name: Optional[str] = None
):
    """Upload a file to a file search store."""
    try:
        if not store_name:
            raise HTTPException(status_code=400, detail="store_name is required")
        
        # Save uploaded file temporarily
        temp_dir = "/tmp/deepy_file_search"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Write file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Upload to file search store
        result = engine.upload_to_file_search(
            temp_path,
            store_name,
            display_name or file.filename
        )
        
        # Clean up
        os.remove(temp_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FileSearchQueryRequest(BaseModel):
    query: str
    store_name: str

class FileSearchQueryResponse(BaseModel):
    answer: str
    citations: List[dict]

@app.post("/file-search/query", response_model=FileSearchQueryResponse)
async def query_file_search(request: FileSearchQueryRequest):
    """Query a file search store."""
    try:
        result = engine.search_in_file_store(request.query, request.store_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file-search/stores")
async def list_file_search_stores():
    """List all file search stores."""
    try:
        stores = []
        for store in engine.client.file_search_stores.list():
            stores.append({
                "name": store.name,
                "display_name": store.display_name if hasattr(store, 'display_name') else "",
                "create_time": str(store.create_time) if hasattr(store, 'create_time') else ""
            })
        return {"stores": stores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

