# Gemini API Documentation Reference

## Models Available

### Text Generation
- `gemini-2.0-flash` - Latest and fastest
- `gemini-1.5-flash` - Fast, good for most tasks
- `gemini-1.5-pro` - More powerful, better reasoning

### Embeddings
- `text-embedding-004` - Latest embedding model
- `gemini-embedding-001` - Previous version

## Key Endpoints

### 1. Generate Content
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

### 2. Embed Content
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent
```

### 3. List Models
```
GET https://generativelanguage.googleapis.com/v1beta/models
```

## Embedding Task Types

- `RETRIEVAL_QUERY` - For search queries
- `RETRIEVAL_DOCUMENT` - For documents being indexed
- `SEMANTIC_SIMILARITY` - For similarity tasks
- `CLASSIFICATION` - For classification
- `CLUSTERING` - For clustering
- `QUESTION_ANSWERING` - For Q&A
- `FACT_VERIFICATION` - For fact checking
- `CODE_RETRIEVAL_QUERY` - For code search

## Current Implementation

Our Deepy backend uses:
- Model: `gemini-1.5-flash` for generation
- Embedding: `text-embedding-004` for embeddings
- Task Type: `retrieval_document` for indexing
- Task Type: `retrieval_query` for searching

## API Key
Stored in `.env` as `GOOGLE_API_KEY`
