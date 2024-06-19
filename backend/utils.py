import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, CollectionConfig, SearchRequest, Payload
from transformers import pipeline, AutoTokenizer, AutoModel
import numpy as np
import hashlib
import uuid
import random
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS, SENTENCE_TRANSFORMER_MODEL, QDRANT_COLLECTION_LENGTH, PIPELINE_MODEL

def get_answer(question):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    tokenizer = AutoTokenizer.from_pretrained(SENTENCE_TRANSFORMER_MODEL)
    model = AutoModel.from_pretrained(SENTENCE_TRANSFORMER_MODEL)

    query_encoding = tokenizer(question, return_tensors="pt")
    query_embedding = model(**query_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten().tolist()

    # Pass query_vector as a separate argument
    results = qdrant_client_instance.search(collection_name=COLLECTION_NAME, query_vector=query_embedding, limit=5)

    context = ""
    for result in results:
        if 'text' in result.payload:
            context += result.payload['text'] + "\n"

    # Generate a response using the context
    qa_pipeline = pipeline("question-answering", model=PIPELINE_MODEL)
    answer = qa_pipeline(question=question, context=context)

    print(answer['answer'])
    return answer['answer']


def add_question_answer_to_qdrant(question, answer):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    collections = qdrant_client_instance.get_collections()
    if COLLECTION_NAME not in [collection.name for collection in collections.collections]:
        config = CollectionConfig(name=COLLECTION_NAME, vector_size=768)
        qdrant_client_instance.create_collection(config=config)

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
                payload={'type': 'question', 'text': question, 'related_answer': answer}
            ),
            PointStruct(
                id=answer_id,
                vector=answer_embedding.tolist(),
                payload={'type': 'answer', 'text': answer, 'related_question': question}
            )
        ]
    )

def get_random_questions_from_collection():
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Get all points from the collection
    query_vector = np.random.rand(QDRANT_COLLECTION_LENGTH)
    points = qdrant_client_instance.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=10)

    # Filter points that are questions
    questions = [point for point in points if point.payload['type'] == 'question']

    # Shuffle the questions and select the first 5
    random.shuffle(questions)
    random_questions = questions[:3]

    return [question.payload['text'] for question in random_questions]

def generate_id(text):
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 10**8
