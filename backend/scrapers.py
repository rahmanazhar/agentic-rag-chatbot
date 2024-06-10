import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, CollectionConfig
import numpy as np
import hashlib
import uuid
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS

def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
        return text
    else:
        return ""

def generate_qna(text):
    headers = {
        'Content-Type': 'application/json'
    }
    prompt = (
        "You are an intelligent assistant. Given the following information from a website, "
        "generate one relevant questions and their corresponding answers. Ensure the answers "
        "are based on the information given and not more than 100 words.\n\n"
        f"Information: {text}\n\n"
        "Write in this format: Question: <question> Answer: <answer>"
    )
    data = {
        'model': MODEL_NAME,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': TEMPERATURE,
        'max_tokens': MAX_TOKENS,
        'stream': False
    }
    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=data, headers=headers)
    if response.status_code == 200:
        
        data = response.json()
        print(data)
        if 'message' in data:
            content = data['message']['content']
            print(content)

            
        return content
    else:
        return ""

def add_question_answer_to_qdrant(question, answer):
    qdrant_client_instance = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    collections = qdrant_client_instance.get_collections()
    if COLLECTION_NAME not in [collection.name for collection in collections.collections]:
        config = CollectionConfig(name=COLLECTION_NAME, vector_size=768)
        qdrant_client_instance.create_collection(config=config)

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

def main(urls):
    for url in urls:
        text = scrape_website(url)
        if text:
            qna = generate_qna(text)
            for qa_pair in qna.split('\n\n'):
                if qa_pair.strip():
                    lines = qa_pair.split('\n')
                    for line in lines:
                        if line.strip().startswith("Question:"):
                            question = line.replace("Question:", "").strip()
                        elif line.strip().startswith("Answer:"):
                            answer = line.replace("Answer:", "").strip()
                    add_question_answer_to_qdrant(question, answer)

if __name__ == "__main__":
    urls = ["https://www.lizard.global/", "https://www.lizard.global/industries/ecommerce", "https://www.lizard.global/services/workshops"]
    main(urls)