from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from qdrant_client import QdrantClient
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Qdrant
from sentence_transformers import SentenceTransformer
import requests
import json

app = Flask(__name__)
CORS(app)

# Setup Qdrant client and vector store
OLLAMA_BASE_URL = 'http://ollama:11434'
MODEL_NAME = 'phi3'

qdrant_client = QdrantClient(host='db', port=6333)
vectorstore = Qdrant(qdrant_client, "rag-chatbot", MODEL_NAME)

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_chat_completion_stream(messages):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "temperature": 1.0,
        "max_tokens": -1
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()
    return response.iter_lines()

def retrieve_documents(query):
    retrieval_chain = RetrievalQA(llm=Ollama(), retriever=vectorstore.as_retriever())
    retrieved_docs = retrieval_chain.retrieve(query)
    return retrieved_docs

def generate_response(query, retrieved_docs):
    messages = [{"role": "user", "content": query}]
    for doc in retrieved_docs:
        messages.append({"role": "system", "content": doc['content']})
    return messages

def add_document_to_qdrant(content):
    vector = embedding_model.encode([content])[0]
    vectorstore.add_documents([{"content": content, "vector": vector}])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    print(f"Received message: {message}")

    # Step 1: Add the user input to Qdrant
    add_document_to_qdrant(message)

    # Step 2: Retrieve documents
    retrieved_docs = retrieve_documents(message)
    
    # Step 3: Generate response
    messages = generate_response(message, retrieved_docs)

    def generate():
        for line in get_chat_completion_stream(messages):
            if line:
                response_data = json.loads(line)
                content = response_data.get('message', {}).get('content', '')
                if content:
                    yield f"data: {content}\n\n"
                if response_data.get('done', False):
                    break

    return Response(generate(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003)
