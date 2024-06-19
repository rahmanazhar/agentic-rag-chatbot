from flask import Blueprint, request, jsonify
from utils import get_answer, add_question_answer_to_qdrant, get_random_questions_from_collection

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

    add_question_answer_to_qdrant(question, answer)
    return jsonify({'message': 'Question and answer added successfully'}), 201


@main_routes.route('/getQuestions', methods=['GET'])
def get_questions():
    random_questions = get_random_questions_from_collection()
    return jsonify({'questions': random_questions}), 201
