# RAG Chatbot Backend

This backend is built using Flask, Ollama, and Qdrant to support a Retrieval-Augmented Generation (RAG) chatbot. The chatbot will take user queries, search for relevant answers, and generate humanized responses.

## File Structure

```
backend/
│
├── app.py
├── routes.py
├── requirements.txt
└── __init__.py
```

## Requirements

- Python 3.7+
- pip (Python package installer)

## Setup

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd backend
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Backend

1. **Run the Flask Application**

   ```bash
   python app.py
   ```

2. **Access the Application**

   The backend will be running at `http://127.0.0.1:5000`.

## API Endpoints

- **POST /ask**

  This endpoint accepts a JSON payload with a user question and returns a humanized response.

  **Request:**

  ```json
  {
    "question": "Your question here"
  }
  ```

  **Response:**

  ```json
  {
    "response": "Humanized response from the chatbot"
  }
  ```
