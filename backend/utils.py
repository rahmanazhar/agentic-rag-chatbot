import ollama
import qdrant_client
import requests
from config import OLLAMA_BASE_URL, MODEL_NAME, COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TEMPERATURE, MAX_TOKENS

def get_chat_completion_stream(messages):
    url = f"{OLLAMA_BASE_URL}/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()
    data = response.json()
    content = data['message']['content'] if 'message' in data else None
    
    return content

def get_answer(question):
    # Initialize Qdrant client
    qdrant_client_instance = qdrant_client.QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Check if the collection exists
    collections = qdrant_client_instance.get_collections()
    if COLLECTION_NAME not in collections:
        return get_chat_completion_stream([{"role": "user", "content": question}])

    # Search for the question
    search_result = qdrant_client_instance.search(collection_name=COLLECTION_NAME, query_vector=question)
    print(search_result)

    if not search_result:
        return get_chat_completion_stream([{"role": "user", "content": question}])

    # Get the most relevant answer based on the search result payload
    answer = None
    max_score = -1
    for result in search_result:
        if result['score'] > max_score:
            answer = result['payload']
            max_score = result['score']

    if answer is None:
        return get_chat_completion_stream([{"role": "user", "content": question}])

    # Using Ollama to humanize the response
    prompt = {
        "messages": [
            {"role": "assistant", "content": "Your are a helpful assistant that answer questions about the following context:"},
            {"role": "user", "content": question},
            {"role": "system", "content": answer}
        ]
    }
    ollama_response = get_chat_completion_stream(prompt)

    return ollama_response['choices'][0]['text']

