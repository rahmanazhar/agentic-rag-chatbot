# agentic-rag-chatbot

## Overview

This project implements an agentic Retrieval-Augmented Generation (RAG) chatbot using Flask for the backend, Next.js for the frontend, Ollama for language model processing, and Qdrant for vector storage. The chatbot supports streaming responses and maintains chat history to provide contextually accurate and up-to-date interactions. The chatbot is designed to dynamically retrieve relevant documents based on user queries and generate responses using these documents, with feedback loops to ensure high-quality outputs.

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node 18+
- Docker and Docker Compose

### Backend Setup

1. **Create a virtual environment and activate it:**
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

2. **Install required Python packages:**
    ```sh
    pip install flask langchain ollama qdrant-client
    ```

### Frontend Setup

3. **Navigate to the `frontend` directory and install dependencies:**
    ```sh
    cd frontend
    npm install
    ```

### Running the Project

4. **From the root directory, build and run the Docker containers:**
    ```sh
    docker-compose up --build
    ```

5. **Run the Ollama model:**
    ```sh
    ollama run phi3
    ```

6. **Access the chatbot at:**
    [http://localhost:3000](http://localhost:3000)

## Project Structure

- **Backend (`backend/app.py`)**: Handles the API endpoints, manages document retrieval and generation using the LangChain library, and integrates with Qdrant for vector storage and Ollama for language model processing.
- **Frontend (`frontend/pages/index.js`)**: Implements the user interface for the chatbot, sending user messages to the backend and displaying streaming responses.
- **Docker Configuration (`docker-compose.yml`)**: Defines the services for the frontend, backend, and Qdrant, and ensures they are properly containerized and networked.

## Key Features

1. **Retrieval-Augmented Generation (RAG)**: 
    - Retrieves relevant documents from Qdrant based on user queries.
    - Uses retrieved documents to generate contextually accurate responses.
    - Incorporates feedback loops to enhance the quality of the generated responses.

2. **Streaming Responses**: 
    - Supports real-time streaming of responses from Ollama to the frontend, providing a seamless chat experience.

3. **Chat History**: 
    - Maintains chat history to ensure the chatbot has context for ongoing conversations, improving the relevance of responses.

4. **Scalability and Modularity**: 
    - Modular architecture with separate frontend and backend components, making it easy to scale and maintain.

## How It Works

1. **User Query**: A user sends a query through the frontend.
2. **Document Retrieval**: The backend retrieves relevant documents from Qdrant using LangChain's retrieval mechanisms.
3. **Response Generation**: The backend generates a response using the retrieved documents and the Ollama language model.
4. **Streaming to Frontend**: The response is streamed to the frontend in real-time, providing immediate feedback to the user.

## Contributions

Contributions are welcome! Feel free to open issues or submit pull requests for improvements or new features.

## License

This project is licensed under the MIT License.
