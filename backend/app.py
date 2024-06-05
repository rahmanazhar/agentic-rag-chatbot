from flask import Flask
from flask_cors import CORS
from routes import main_routes

app = Flask(__name__)
CORS(app) 
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3003, debug=True)
