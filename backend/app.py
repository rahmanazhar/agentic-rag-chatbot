from flask import Flask
from flask_cors import CORS
from routes import main_routes
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from config import COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_LENGTH

app = Flask(__name__)
CORS(app) 
app.register_blueprint(main_routes)

if __name__ == "__main__":
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        collections = qdrant_client_instance.get_collections().collections
    except Exception as e:
        print(f"Failed to get collections: {e}")
        collections = []

    if COLLECTION_NAME not in collections:
        try:
            qdrant_client_instance.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=QDRANT_COLLECTION_LENGTH, distance=Distance.COSINE),
            )
        except Exception as e:
            print(f"Failed to create collection: {e}")
    app.run(host='0.0.0.0', port=3003, debug=True)
