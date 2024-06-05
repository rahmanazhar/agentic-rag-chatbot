from flask import Blueprint, request, jsonify
from utils import get_answer
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
import numpy as np
from qdrant_client.models import PointStruct

import uuid

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

    # Generate a random vector for the question and answer
    vector = np.random.rand(384).tolist()

    # Generate a UUID for the id
    point_id = str(uuid.uuid4())

    # Upsert the question and answer into the Qdrant collection
    qdrant_client_instance.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={'question': question, 'answer': answer}
            )
        ]
    )

    return jsonify({'message': 'Question and answer added successfully'}), 201
