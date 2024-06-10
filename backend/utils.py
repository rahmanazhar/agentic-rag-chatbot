import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from transformers import AutoTokenizer, AutoModel
import numpy as np
import hashlib
import uuid
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS, SENTENCE_TRANSFORMER_MODEL, QDRANT_COLLECTION_LENGTH

def get_answer(question):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Ensure the collection exists
    collections = qdrant_client_instance.get_collections()
    if COLLECTION_NAME not in [collection.name for collection in collections.collections]:
        return "Sorry, I couldn't find any relevant information."

    # Tokenize and encode the question
    tokenizer = AutoTokenizer.from_pretrained(SENTENCE_TRANSFORMER_MODEL)
    model = AutoModel.from_pretrained(SENTENCE_TRANSFORMER_MODEL)
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

    return best_answer

def add_question_answer_to_qdrant(question, answer):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    tokenizer = AutoTokenizer.from_pretrained(SENTENCE_TRANSFORMER_MODEL)
    model = AutoModel.from_pretrained(SENTENCE_TRANSFORMER_MODEL)

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
