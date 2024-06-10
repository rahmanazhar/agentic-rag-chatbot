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
        "generate several relevant questions and their corresponding answers. The questions should "
        "be comprehensive and cover the key points mentioned in the information. Ensure the answers "
        "are accurate and concise.\n\n"
        f"Information: {text}\n\n"
        "Q&A:"
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
        result = response.json()[0]['message']['content']
        print(result)
        return result
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
    print("Starting scraping process...")
    for url in urls:
        print(f"Scraping website: {url}")
        text = scrape_website(url)
        if text:
            print("Generating Q&A...")
            qna = generate_qna(text)
            for qa_pair in qna.split('\n\n'):
                if qa_pair.strip():
                    question, answer = qa_pair.split('\n')
                    print(f"Adding question: {question}")
                    add_question_answer_to_qdrant(question.strip(), answer.strip())
    print("Scraping process completed.")

if __name__ == "__main__":
    urls = ["https://www.lizard.global/", "https://www.lizard.global/industries/ecommerce", "https://www.lizard.global/services/workshops"]
    main(urls)