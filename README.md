# agentic-rag-chatbot

python -m venv venv
source venv/bin/activate
pip install flask langchain ollama qdrant-client

From the root directory, run Docker Compose:
docker-compose up --build

After run
ollama pull llama3

http://localhost:3000