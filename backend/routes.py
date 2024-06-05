from flask import Blueprint, request, jsonify
from utils import get_answer
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
import numpy as np
from qdrant_client.models import PointStruct

from transformers import AutoTokenizer, AutoModel

import uuid
import hashlib

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    answer = get_answer(question)
    return jsonify({'answer': answer})


@main_routes.route('/add-qa', methods=['POST'])
def add_qa():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({'error': 'Question and answer are required'}), 400

    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Use a pre-trained tokenizer and model to convert text to vectors
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    # Encode the question and answer using the tokenizer
    question_encoding = tokenizer(question, return_tensors="pt")
    answer_encoding = tokenizer(answer, return_tensors="pt")

    # Calculate the embeddings for the question and answer
    question_embedding = model(**question_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten()
    answer_embedding = model(**answer_encoding).last_hidden_state.mean(dim=1).detach().numpy().flatten()

    # Generate an ID for the question and answer
    question_id = generate_id(question)
    answer_id = generate_id(answer)

    # Upsert the question and answer into the Qdrant collection
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

    return jsonify({'message': 'Question and answer added successfully'}), 201

def generate_id(text):
    # Use a hash function to generate a unique integer ID
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 10**8
