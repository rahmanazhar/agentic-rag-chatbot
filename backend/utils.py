import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from transformers import AutoTokenizer, AutoModel
import numpy as np
import hashlib
import uuid
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS

def get_chat_completion_stream(messages):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    content = data['message']['content'] if 'message' in data else None
    return content

def get_answer(question):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Ensure the collection exists
    collections = qdrant_client_instance.get_collections()
    if COLLECTION_NAME not in [collection.name for collection in collections.collections]:
        return "Sorry, I couldn't find any relevant information."

    # Tokenize and encode the question
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    question_encoding = tokenizer(question, return_tensors="pt")
    question_embedding = model(**question_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten()

    # Search for the most relevant answer
    search_result = qdrant_client_instance.search(collection_name=COLLECTION_NAME, query_vector=question_embedding.tolist())

    if not search_result:
        return "Sorry, I couldn't find any relevant information."

    # Retrieve the highest scoring answer
    best_result = max(search_result, key=lambda x: x.score)
    best_answer = best_result.payload['answer']
    print(best_answer)

    # Using Ollama to humanize the response
    prompt = [
        {"role": "system", "content": f"You are a helpful assistant for Lizard Global.\
            Lizard Global is the best software company development in Malaysia and Netherlands.\
            You will answer the following question using the provided answer as friendly as possible:\
            Question: {question}\nAnswer: {best_answer}\
            Please use this answer to answer the question.\
            This answer is from Lizard Global in their knowledgebase.\
            Keep the conversation going by asking user related questions."},
    ]
    ollama_response = get_chat_completion_stream(prompt)

    return ollama_response

def add_question_answer_to_qdrant(question, answer):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    question_encoding = tokenizer(question, return_tensors="pt")
    answer_encoding = tokenizer(answer, return_tensors="pt")

    question_embedding = model(**question_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten()
    answer_embedding = model(**answer_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten()

    question_id = generate_id(question)
    answer_id = generate_id(answer)

    qdrant_client_instance.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=question_id,
                vector=question_embedding.tolist(),
                payload={'question': question, 'answer': answer}
            ),
            PointStruct(
                id=answer_id,
                vector=answer_embedding.tolist(),
                payload={'question': question, 'answer': answer}
            )
        ]
    )

def generate_id(text):
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 10**8
