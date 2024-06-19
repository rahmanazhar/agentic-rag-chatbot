import requests
from bs4 import BeautifulSoup, SoupStrainer
from transformers import AutoTokenizer, AutoModel, pipeline
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, CollectionConfig, SearchRequest, Payload
import numpy as np
import hashlib
import uuid
import os
from urllib.parse import urljoin, urlparse
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS, SENTENCE_TRANSFORMER_MODEL, PIPELINE_MODEL

FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.exe']

def is_valid_url(url):
    parsed_url = urlparse(url)
    return not any(parsed_url.path.lower().endswith(ext) for ext in FILE_EXTENSIONS)

def scrape_website(url, visited=set(), depth=1, max_depth=10):
    print(f"Scraping {url}")
    if depth > max_depth or url in visited or not is_valid_url(url):
        return ""

    response = requests.get(url)
    if response.status_code != 200:
        return ""

    visited.add(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join(p.get_text() for p in soup.find_all('p'))

    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        if full_url.startswith(url):
            text += scrape_website(full_url, visited, depth + 1, max_depth)

    return text

def save_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def load_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def generate_qna(text):
    headers = {
        'Content-Type': 'application/json'
    }
    prompt = (
        "You are an intelligent assistant. Given the following information from a website, "
        "generate about 20 relevant questions that users might have and their corresponding answers. "
        "Ensure the answers are based on the information given and not more than 100 words each.\n\n"
        f"Information: {text}\n\n"
        "Write in this format: Question: <question> Answer: <answer> Separate each question-answer pair by a newline."
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
        if 'message' in data:
            content = data['message']['content']
            return content
    return ""

def add_question_answer_to_qdrant(question, answer):
    print(f"Adding question: {question} and answer: {answer} to Qdrant")
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

def generate_id(text):
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 10**8

def main(url):
    scraped_text = scrape_website(url)
    if scraped_text:
        filename = 'scraped_content.txt'
        save_to_file(filename, scraped_text)
                        
def load_generate_qna():
    print("Loading and generating QnA")
    filename = 'scraped_content.txt'
    loaded_text = load_from_file(filename)
    qna = generate_qna(loaded_text)
    if qna:
        for qa_pair in qna.split('\n\n'):
            if qa_pair.strip():
                lines = qa_pair.split('\n')
                question = ""
                answer = ""
                for line in lines:
                    if line.strip().startswith("Question:"):
                        question = line.replace("Question:", "").strip()
                    elif line.strip().startswith("Answer:"):
                        answer = line.replace("Answer:", "").strip()
                if question and answer:
                    add_question_answer_to_qdrant(question, answer)

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    main(url)
    load_generate_qna()
