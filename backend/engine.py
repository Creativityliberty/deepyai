import os
import chromadb
import pathlib
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional, Union

class DeepyEngine:
    def __init__(self, api_key: str, db_path: str = "./deepy_db"):
        self.api_key = api_key
        self.db_path = db_path
        
        # Initialize Gemini client (for generation only)
        self.client = genai.Client(api_key=api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Use ChromaDB's default embedding (FAST and no API calls!)
        print("🚀 Initializing ChromaDB with default embeddings...")
        
        # Get or create collection with default embedding
        self.collection = self.chroma_client.get_or_create_collection(
            name="design_docs_v2"  # New collection name to avoid conflicts
        )
        print("✅ Ready to ingest!")


    
    def ingest_file(self, file_path: str):
        """Ingest a file by splitting it into chunks"""
        print(f"📄 Reading {os.path.basename(file_path)}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's an "Awesome" format (multiple files in one)
        if "================" in content:
            return self._ingest_awesome_format(content, file_path)
        else:
            return self._ingest_single_file(content, file_path)
    
    def _ingest_awesome_format(self, content: str, source_path: str):
        """Parse and ingest Awesome format with multiple files - OPTIMIZED"""
        print("🔍 Detected Awesome format, parsing...")
        files = content.split("================")
        
        # Prepare batch data
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        for file_idx, file_block in enumerate(files):
            if not file_block.strip():
                continue
            
            lines = file_block.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # First line is the file path
            file_header = lines[0].strip()
            if file_header.startswith("FILE:"):
                file_name = file_header.replace("FILE:", "").strip()
            else:
                file_name = f"section_{file_idx}"
            
            # Rest is content
            file_content = '\n'.join(lines[1:])
            
            # Split into LARGER chunks (3000 chars instead of 1000) = fewer API calls
            chunks = self._split_into_chunks(file_content, chunk_size=3000, overlap=300)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": file_name,
                    "original_file": os.path.basename(source_path),
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                }
                doc_id = f"{file_name.replace('/', '_')}_{i}"
                
                all_documents.append(chunk)
                all_metadatas.append(metadata)
                all_ids.append(doc_id)
        
        print(f"📦 Prepared {len(all_documents)} chunks, starting batch ingestion...")
        
        # Batch insert (MUCH faster!)
        if all_documents:
            batch_size = 100
            total_batches = (len(all_documents) - 1) // batch_size + 1
            
            for i in range(0, len(all_documents), batch_size):
                batch_docs = all_documents[i:i+batch_size]
                batch_metas = all_metadatas[i:i+batch_size]
                batch_ids = all_ids[i:i+batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                current_batch = i // batch_size + 1
                print(f"✅ Batch {current_batch}/{total_batches} indexed ({len(batch_docs)} chunks)")
        
        print(f"🎉 Total indexed: {len(all_documents)} chunks")
        return len(all_documents)
    
    def _ingest_single_file(self, content: str, file_path: str):
        """Ingest a single file by chunking - OPTIMIZED"""
        chunks = self._split_into_chunks(content, chunk_size=3000, overlap=300)
        print(f"📦 Split into {len(chunks)} chunks")
        
        # Batch insert
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": os.path.basename(file_path),
                "chunk_id": i,
                "total_chunks": len(chunks)
            }
            doc_id = f"{os.path.basename(file_path).replace('.', '_')}_{i}"
            
            documents.append(chunk)
            metadatas.append(metadata)
            ids.append(doc_id)
        
        if documents:
            print(f"💾 Indexing {len(documents)} chunks...")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Indexed successfully!")
        
        return len(chunks)
    
    def _split_into_chunks(self, text: str, chunk_size: int = 3000, overlap: int = 300):
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at a newline
            if end < len(text):
                last_newline = chunk.rfind('\n')
                if last_newline > chunk_size // 2:
                    chunk = chunk[:last_newline]
                    end = start + last_newline
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]
    
    def search(self, query: str, n_results: int = 3):
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        sources = []
        for i in range(len(results['documents'][0])):
            sources.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            })
        
        return sources
    
    def generate_answer(self, question: str, context_docs: list):
        """Generate an answer using Gemini with context"""
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Source: {doc['metadata'].get('source', 'unknown')}\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Create prompt
        prompt = f"""Tu es Deepy, un assistant expert en architecture logicielle et design patterns.

Contexte pertinent:
{context}

Question: {question}

Réponds de manière claire et détaillée en te basant sur le contexte fourni. Si le contexte ne contient pas l'information, dis-le clairement."""
        
        # Generate response using Gemini 2.0 Flash Experimental
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        
        return response.text
    
    def chat(self, question: str):
        """Main chat function: search + generate"""
        # Search for relevant context
        sources = self.search(question, n_results=5)
        
        # Generate answer
        answer = self.generate_answer(question, sources)
        
        # Format sources for response
        formatted_sources = [
            {
                "name": src['metadata'].get('source', 'unknown'),
                "content": src['content']
            }
            for src in sources
        ]
        
        return {
            "answer": answer,
            "sources": formatted_sources
        }
    
    def process_pdf(self, pdf_path: str, prompt: str = "Summarize this document") -> dict:
        """Process a PDF file using Gemini's native PDF understanding.
        
        Args:
            pdf_path: Path to the PDF file
            prompt: Question or instruction for the PDF
            
        Returns:
            dict with 'answer' and 'file_info'
        """
        print(f"📄 Processing PDF: {os.path.basename(pdf_path)}...")
        
        # Read PDF as bytes
        pdf_file = pathlib.Path(pdf_path)
        pdf_bytes = pdf_file.read_bytes()
        
        # Check file size
        file_size_mb = len(pdf_bytes) / (1024 * 1024)
        print(f"📦 File size: {file_size_mb:.2f} MB")
        
        # For files > 20MB, use Files API for better performance
        if file_size_mb > 20:
            print("📤 Uploading to Files API (large file)...")
            uploaded_file = self.client.files.upload(
                file=pdf_path,
            )
            print(f"✅ Uploaded: {uploaded_file.name}")
            
            # Generate content using uploaded file
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[uploaded_file, prompt]
            )
            
            file_info = {
                "name": uploaded_file.name,
                "size_mb": file_size_mb,
                "uri": uploaded_file.uri if hasattr(uploaded_file, 'uri') else None
            }
        else:
            # For smaller files, use inline data
            print("📝 Processing inline (small file)...")
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[
                    types.Part.from_bytes(
                        data=pdf_bytes,
                        mime_type='application/pdf',
                    ),
                    prompt
                ]
            )
            
            file_info = {
                "name": os.path.basename(pdf_path),
                "size_mb": file_size_mb,
            }
        
        print("✅ PDF processed successfully!")
        return {
            "answer": response.text,
            "file_info": file_info
        }
    
    def generate_structured_output(
        self,
        text: str,
        schema: Union[type[BaseModel], dict],
        prompt: Optional[str] = None
    ) -> BaseModel:
        """Generate structured output conforming to a Pydantic schema.
        
        Args:
            text: Input text to process
            schema: Pydantic model class or JSON schema dict
            prompt: Optional custom prompt (default: "Extract information from this text")
            
        Returns:
            Validated Pydantic model instance
        """
        # Build prompt
        if prompt is None:
            prompt = "Extract the requested information from the following text:"
        
        full_prompt = f"{prompt}\n\n{text}"
        
        # Get JSON schema
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            json_schema = schema.model_json_schema()
            schema_class = schema
        else:
            json_schema = schema
            schema_class = None
        
        print(f"🔍 Generating structured output...")
        
        # Generate with structured output
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=json_schema,
            )
        )
        
        print("✅ Structured output generated!")
        
        # Parse and validate if we have a Pydantic class
        if schema_class:
            return schema_class.model_validate_json(response.text)
        else:
            # Return raw JSON if no Pydantic class
            import json
            return json.loads(response.text)
    
    def execute_code(self, prompt: str) -> dict:
        """Execute Python code using Gemini's code execution tool.
        
        Args:
            prompt: Question or task that requires code execution
            
        Returns:
            dict with 'text', 'code', and 'output' parts
        """
        print(f"💻 Executing code for: {prompt[:50]}...")
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution)]
            )
        )
        
        result = {
            "text_parts": [],
            "code_parts": [],
            "output_parts": []
        }
        
        # Parse response parts
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                result["text_parts"].append(part.text)
            if hasattr(part, 'executable_code') and part.executable_code is not None:
                result["code_parts"].append({
                    "language": part.executable_code.language if hasattr(part.executable_code, 'language') else "PYTHON",
                    "code": part.executable_code.code
                })
            if hasattr(part, 'code_execution_result') and part.code_execution_result is not None:
                result["output_parts"].append({
                    "outcome": part.code_execution_result.outcome if hasattr(part.code_execution_result, 'outcome') else "OUTCOME_OK",
                    "output": part.code_execution_result.output
                })
        
        print("✅ Code execution completed!")
        return result
    
    def analyze_urls(self, prompt: str, urls: list[str]) -> dict:
        """Analyze content from URLs using Gemini's URL context tool.
        
        Args:
            prompt: Question or instruction about the URLs
            urls: List of URLs to analyze (max 20)
            
        Returns:
            dict with 'answer' and 'url_metadata'
        """
        print(f"🌐 Analyzing {len(urls)} URL(s)...")
        
        # Build prompt with URLs
        url_text = " and ".join(urls)
        full_prompt = f"{prompt} {url_text}"
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(url_context={})]
            )
        )
        
        # Extract URL metadata if available
        url_metadata = []
        if hasattr(response.candidates[0], 'url_context_metadata'):
            metadata = response.candidates[0].url_context_metadata
            if hasattr(metadata, 'url_metadata'):
                for url_meta in metadata.url_metadata:
                    url_metadata.append({
                        "url": url_meta.retrieved_url if hasattr(url_meta, 'retrieved_url') else "",
                        "status": url_meta.url_retrieval_status if hasattr(url_meta, 'url_retrieval_status') else "UNKNOWN"
                    })
        
        print("✅ URL analysis completed!")
        return {
            "answer": response.text,
            "url_metadata": url_metadata
        }
    
    def create_file_search_store(self, display_name: str) -> str:
        """Create a new file search store.
        
        Args:
            display_name: Name for the file search store
            
        Returns:
            Store name (ID)
        """
        print(f"📁 Creating file search store: {display_name}...")
        
        store = self.client.file_search_stores.create(
            config={'display_name': display_name}
        )
        
        print(f"✅ Created store: {store.name}")
        return store.name
    
    def upload_to_file_search(self, file_path: str, store_name: str, display_name: str = None) -> dict:
        """Upload a file to a file search store.
        
        Args:
            file_path: Path to the file to upload
            store_name: Name of the file search store
            display_name: Optional display name for the file
            
        Returns:
            dict with operation status
        """
        import time
        
        print(f"📤 Uploading {os.path.basename(file_path)} to file search store...")
        
        config = {}
        if display_name:
            config['display_name'] = display_name
        
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=store_name,
            config=config
        )
        
        # Wait for operation to complete
        while not operation.done:
            time.sleep(2)
            operation = self.client.operations.get(operation)
        
        print("✅ Upload completed!")
        return {"status": "completed", "operation_name": operation.name}
    
    def search_in_file_store(self, query: str, store_name: str) -> dict:
        """Search for information in a file search store.
        
        Args:
            query: Search query
            store_name: Name of the file search store
            
        Returns:
            dict with 'answer' and 'citations'
        """
        print(f"🔍 Searching in file store for: {query[:50]}...")
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=query,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ]
            )
        )
        
        # Extract grounding metadata (citations)
        citations = []
        if hasattr(response.candidates[0], 'grounding_metadata'):
            grounding = response.candidates[0].grounding_metadata
            if hasattr(grounding, 'grounding_chunks'):
                for chunk in grounding.grounding_chunks:
                    citations.append({
                        "source": chunk.source if hasattr(chunk, 'source') else "Unknown",
                        "content": chunk.content if hasattr(chunk, 'content') else ""
                    })
        
        print("✅ File search completed!")
        return {
            "answer": response.text,
            "citations": citations
        }
