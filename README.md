

# Lawbridge – Your Intelligent Legal Assistant

[](https://opensource.org/licenses/MIT)
[](https://www.python.org/)
[](https://flask.palletsprojects.com/)
[](https://www.langchain.com/)

Welcome to Lawbridge, a sophisticated, context-aware legal chatbot designed to provide users with accurate and quick legal information. It leverages a powerful **Retrieval-Augmented Generation (RAG)** system to deliver human-like, contextually appropriate responses, acting as a first point of reference for legal queries.

##  Key Features

  * **Context-Aware Responses**: Utilizes a RAG system built with **LangChain** for high accuracy and relevance.
  * **High-Performance AI**: Integrates **HuggingFace** and **Cohere** models to generate precise answers.
  * **Fast & Efficient**: Delivers responses with an average time of just **3 seconds** per query.
  * **User Authentication**: Secure user registration and login system, including a "Continue with Google" option.
  * **Chat History**: Allows users to view and revisit their past legal queries and the responses received.
  * **Admin Interface**: Separate login portal for administrative management.
  * **Robust Backend**: Powered by a **Flask** backend with over 10 dedicated API endpoints.
  * **Scalable Database**: Manages all user profiles and chat histories efficiently using **Google Firebase**.

-----



##  Tech Stack & Architecture

The core of Lawbridge is its **Retrieval-Augmented Generation (RAG)** architecture, which ensures that the chatbot's responses are not just fluent but also factually grounded in a specific knowledge base.

1.  **Backend**: **Flask** serves as the web framework, handling routing, requests, and business logic.
2.  **Frontend**: **Jinja2 Templates** are used to dynamically render the user interface.
3.  **AI Orchestration**: **LangChain** orchestrates the complex workflow of the RAG system.
4.  **AI Models**: The system leverages cutting-edge models from **HuggingFace** and **Cohere** for natural language understanding and generation.
5.  **Database**: **Google Firebase** is used for its real-time capabilities to store and manage user data and chat histories.

-----

##  Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

  * Python 3.9+
  * Pip package manager

### Installation

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/rockingyash1717/lawbridge.git
    ```

2.  **Navigate to the project directory:**

    ```sh
    cd lawbridge
    ```

3.  **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API keys and configuration details.

    ```.env
    # Firebase Configuration
    FIREBASE_API_KEY="YOUR_API_KEY"
    FIREBASE_AUTH_DOMAIN="YOUR_AUTH_DOMAIN"
    # ... other Firebase config

    # Cohere API Key
    COHERE_API_KEY="YOUR_COHERE_API_KEY"

    # HuggingFace API Key
    HUGGINGFACE_API_KEY="YOUR_HUGGINGFACE_API_KEY"
    ```

5.  **Run the application:**

    ```sh
    flask run
    ```

    The application will be available at `http://127.0.0.1:5000`.

-----

##  API Endpoints

The Flask backend exposes over 10 API endpoints to handle all frontend interactions, including:

  * `/` - Home page
  * `/login` - User login
  * `/signup` - User registration
  * `/chat` - Handles chat requests and AI responses
  * `/history` - Retrieves user's chat history
  * `/logout` - Logs the user out
  * `/admin` - Admin login page

-----

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

-----

## 👨‍💻 Author


  * GitHub: [@rockingyash1717](https://www.google.com/search?q=https://github.com/rockingyash1717)

-----
