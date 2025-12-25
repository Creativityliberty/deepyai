# Google GenAI SDK - Complete Documentation

> **Source**: https://googleapis.github.io/python-genai/
> **Version**: Latest (2025)
> **Purpose**: Complete reference for Google Gemini API integration

## Installation

```bash
pip install google-genai
# With uv:
uv pip install google-genai
```

## Quick Start

```python
from google import genai
from google.genai import types

# Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')

# Vertex AI API
client = genai.Client(
    vertexai=True, 
    project='your-project-id', 
    location='us-central1'
)
```

## Environment Variables

```bash
# Gemini Developer API
export GEMINI_API_KEY='your-api-key'
# or
export GOOGLE_API_KEY='your-api-key'

# Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

## Core Features

### 1. Generate Content

**Text Generation**:
```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)
```

**Image Generation**:
```python
response = client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents='A cartoon infographic for flying sneakers',
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="9:16"),
    ),
)
for part in response.parts:
    if part.inline_data:
        generated_image = part.as_image()
        generated_image.show()
```

**With File Upload**:
```python
file = client.files.upload(file='document.pdf')
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=['Summarize this file', file]
)
```

### 2. Streaming

**Synchronous Streaming**:
```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

**Asynchronous Streaming**:
```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story'
):
    print(chunk.text, end='')
```

### 3. Function Calling

**Automatic Function Calling**:
```python
def get_current_weather(location: str) -> str:
    """Returns the current weather.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)
print(response.text)
```

**Manual Function Declaration**:
```python
function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g. San Francisco, CA',
            }
        },
        'required': ['location'],
    },
)

tool = types.Tool(function_declarations=[function])
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)
```

### 4. Structured Outputs

**JSON Schema**:
```python
user_profile = {
    'properties': {
        'age': {'type': 'integer', 'minimum': 0, 'maximum': 20},
        'username': {'type': 'string', 'description': "User's unique name"},
    },
    'required': ['username', 'age'],
    'type': 'object',
}

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me a random user profile.',
    config={
        'response_mime_type': 'application/json',
        'response_json_schema': user_profile
    },
)
print(response.parsed)
```

**Pydantic Models**:
```python
from pydantic import BaseModel

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
```

**Enum Responses**:
```python
from enum import Enum

class InstrumentEnum(Enum):
    PERCUSSION = 'Percussion'
    STRING = 'String'
    WOODWIND = 'Woodwind'
    BRASS = 'Brass'
    KEYBOARD = 'Keyboard'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What instrument plays multiple notes at once?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': InstrumentEnum,
    },
)
```

### 5. Code Execution

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Calculate the sum of first 20 prime numbers',
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution={})],
    ),
)
```

### 6. URL Context

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Compare these websites',
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context={})],
    ),
)
```

### 7. File Search

**Create Store**:
```python
store = client.file_search_stores.create(
    display_name='My Knowledge Base'
)
```

**Upload Files**:
```python
document = client.file_search_stores.upload(
    store_name=store.name,
    file='document.pdf'
)
```

**Query Store**:
```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What are the key points?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )],
    ),
)
```

### 8. Chat Sessions

```python
chat = client.chats.create(model='gemini-2.5-flash')
response = chat.send_message('tell me a story')
print(response.text)

response = chat.send_message('summarize the story in 1 sentence')
print(response.text)
```

### 9. Caching

```python
cached_content = client.caches.create(
    model='gemini-2.5-flash',
    config=types.CreateCachedContentConfig(
        contents=[types.Content(
            role='user',
            parts=[types.Part.from_uri(
                file_uri='gs://path/to/file.pdf',
                mime_type='application/pdf'
            )],
        )],
        system_instruction='Analyze this document',
        ttl='3600s',
    ),
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize the document',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    ),
)
```

### 10. Embeddings

```python
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents='why is the sky blue?',
)
print(response)

# Multiple contents with config
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)
```

### 11. Image Generation (Imagen)

```python
response = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt='An umbrella in the foreground, and a rainy night sky',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response.generated_images[0].image.show()
```

### 12. Video Generation (Veo)

```python
operation = client.models.generate_videos(
    model='veo-2.0-generate-001',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

# Poll operation
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

### 13. Tuning (Vertex AI only)

```python
tuning_job = client.tunings.tune(
    base_model='gemini-2.5-flash',
    training_dataset=types.TuningDataset(
        gcs_uri='gs://bucket/training-data.jsonl',
    ),
    config=types.CreateTuningJobConfig(
        epoch_count=1,
        tuned_model_display_name='my-tuned-model'
    ),
)
```

### 14. Batch Prediction

```python
job = client.batches.create(
    model='gemini-2.5-flash',
    src='bq://project.dataset.table',  # or gs://path/to/file
)

# Wait for completion
while job.state not in ['JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED']:
    job = client.batches.get(name=job.name)
    time.sleep(30)
```

## Advanced Configuration

### Safety Settings

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Say something',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            )
        ]
    ),
)
```

### Generation Config

```python
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=100,
        temperature=0.3,
        top_p=0.95,
        top_k=20,
        seed=5,
        stop_sequences=['STOP!'],
        presence_penalty=0.0,
        frequency_penalty=0.0,
    ),
)
```

### HTTP Options

```python
from google.genai import types

client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(
        api_version='v1',  # or 'v1alpha'
        timeout=60,
        retry_options=types.HttpRetryOptions(
            attempts=3,
            initial_delay=1.0,
            max_delay=10.0,
        ),
    )
)
```

### Proxy Configuration

```bash
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='client.pem'
```

## Error Handling

```python
from google.genai import errors

try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code)  # 404
    print(e.message)
```

## Best Practices

1. **Use context managers** for automatic cleanup:
```python
with Client() as client:
    response = client.models.generate_content(...)
```

2. **Use async for better performance**:
```python
async with Client().aio as aclient:
    response = await aclient.models.generate_content(...)
```

3. **Cache frequently used content**:
```python
cached_content = client.caches.create(...)
# Reuse cached_content.name in multiple requests
```

4. **Use streaming for long responses**:
```python
for chunk in client.models.generate_content_stream(...):
    print(chunk.text, end='')
```

5. **Implement proper error handling**:
```python
try:
    response = client.models.generate_content(...)
except errors.APIError as e:
    # Handle API errors
    pass
```

## Models Available

- `gemini-2.5-flash` - Fast, efficient model
- `gemini-2.5-pro` - Most capable model
- `gemini-2.0-flash-exp` - Experimental features
- `gemini-embedding-001` - Embeddings
- `imagen-3.0-generate-002` - Image generation
- `veo-2.0-generate-001` - Video generation

## Token Limits

- **Input tokens**: Model-specific (check with `model.input_token_limit`)
- **Output tokens**: Configurable via `max_output_tokens`
- **Cached tokens**: Up to 1M tokens with caching

## Rate Limits

Varies by API tier and model. Use retry logic and exponential backoff.

---

**Complete API Reference**: https://googleapis.github.io/python-genai/
