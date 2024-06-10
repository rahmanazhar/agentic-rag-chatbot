# agentic-rag-chatbot

## Description

This project is a retrieval-augmented generation (RAG) chatbot that leverages Qdrant for vector storage and retrieval, Ollama for language model interactions, and SentenceTransformers for generating embeddings. The chatbot can store user inputs, retrieve relevant documents, and generate contextually appropriate responses.

## Setup

### Environment Setup

1. Create a virtual environment:
    ```bash
    python -m venv venv #or python3 -m venv venv
    source venv/bin/activate
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Docker Setup

1. From the root directory, run Docker Compose:
    ```bash
    docker-compose up --build
    ```

2. Run Ollama:
    ```bash
    ollama run llama2
    ```

## Usage

1. Start the Flask app:
    ```bash
    python app.py
    ```

2. Access the chatbot at:
    ```
    http://localhost:3003
    ```

## Qdrant Collection Setup

To create the `rag-chatbot` collection in Qdrant, use the following Python script:

```python
from qdrant_client import QdrantClient

client = QdrantClient(host='db', port=6333)

# Define the schema for the collection
schema = {
    "vectors": {
        "size": 384,  # Size of the vectors from the embedding model
        "distance": "Cosine"  # Distance metric for vector similarity
    }
}

# Create the collection
client.create_collection(
    collection_name="rag-chatbot",
    vectors_config=schema
)
