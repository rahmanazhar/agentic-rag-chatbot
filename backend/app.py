from flask import Flask, request, jsonify
from langchain.llms import Ollama
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

app = Flask(__name__)
ollama = Ollama()
qdrant_client = QdrantClient(host='db', port=6333)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    response = ollama.generate(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
