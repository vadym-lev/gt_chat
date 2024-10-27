# GT Chat API

## Table of Contents
- [Setup and Installation](#setup-and-installation)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Containers](#containers)

## Setup and Installation

### Requirements
- Docker
- Docker Compose
### Installation Steps

1. **Clone the repository** and navigate to the project directory:
    ```bash
    git clone https://github.com/vadym-lev/gt_chat.git
    cd gt_chat
    ```
2. **Build and Start Containers**: Run the following command to build and start the services:
   ```bash
   docker-compose up --build
   ```
3. **Stop the Application**: To stop the containers, run:
   ```bash
   docker-compose down
   ```

## Database Models
The application has a single Task model that represents each text processing task. Below are the model fields and their characteristics.

### Task Model:
- **task_id** (UUID): Unique identifier for the task.
- **original_text** (String): The original text data received from the user.
- **processed_text** (String): The text after processing (e.g., cleaning).
- **type** (Enum): The type of text, limited to "chat_item", "summary", or "article".
- **word_count** (Integer): Number of words in the processed text.
- **language** (String): Detected language code (e.g., 'en' for English).
- **status** (String): Status of the task, either "processing" or "completed".

## API Endpoints

### 1. POST /process-text
This endpoint receives a JSON payload containing text data to be processed asynchronously. The payload should include the `text` field and the `type` field indicating the nature of the text.

#### Request Body:
- **type** (String): Must be one of "chat_item", "summary", or "article".
  - "chat_item": Text up to 300 characters.
  - "summary": Text up to 3000 characters.
  - "article": Text over 300,000 characters.
- **text** (String): The text content to process.

#### Response:
- **task_id** (UUID): Unique identifier for the task.
- **status** (String): Processing status (always "processing").

#### Example Request:
```bash
curl -X POST "http://localhost:8000/process-text"      -H "Content-Type: application/json"      -d '{"text": "Hello world!", "type": "chat_item"}'
```

#### Example Response:
```json
{
  "task_id": "b6a7f1a2-3c4d-5e6f-7890-1a2b3c4d5e6f",
  "status": "processing"
}
```

### 2. GET /results/{task_id}
Retrieve the results of a processed task by its `task_id`.

#### Path Parameter:
- **task_id** (UUID): Unique identifier for the task.

#### Response:
- **task_id** (UUID): Task identifier.
- **original_text** (String): Original text submitted by the user.
- **processed_text** (String): Text after processing.
- **word_count** (Integer): Word count of processed text.
- **language** (String): Detected language.
- **status** (String): Processing status.

#### Example Request:
```bash
curl -X GET "http://localhost:8000/results/b6a7f1a2-3c4d-5e6f-7890-1a2b3c4d5e6f"
```

#### Example Response:
```json
{
  "task_id": "b6a7f1a2-3c4d-5e6f-7890-1a2b3c4d5e6f",
  "original_text": "Hello world!",
  "processed_text": "Hello world!",
  "word_count": 2,
  "language": "en",
  "status": "completed"
}
```


## Testing
The project includes unit tests for both the API and worker service. The tests check various aspects, including endpoint responses and worker processing behavior.

### Run API Tests:
```bash
docker-compose exec fastapi_app pytest /app/tests/test_api.py
```

### Run Worker Tests:
```bash
docker-compose exec worker pytest /app/tests/test_worker.py
```

### Test Coverage
#### API Tests:
- `test_process_text`: Validates the `/process-text` endpoint, checking for correct task creation and response.
- `test_get_results_not_found`: Tests the `/results/{task_id}` endpoint for a non-existent task, ensuring a 404 response.
- `test_get_results_completed`: Verifies retrieval of a completed task's data.

#### Worker Tests:
- `test_clean_text`: Verifies that the worker processes a task correctly by checking the addition and commit of data in the database mock.

## Containers
This project includes the following Docker containers:
- **fastapi_app**: Hosts the FastAPI application, exposing endpoints for processing and retrieving text data.
- **rabbitmq**: Provides the RabbitMQ message broker for task queuing.
- **worker**: Worker service that consumes messages from RabbitMQ, processes the text, and updates the database with results.

I have isolated the worker into a separate container for scalability. So that the API and the worker container can work with SQL Lite, I will place the database in volumes `/shared_data:/app/shared_data`

In my opinion, it is best to use PostgreSQL and put the database in a separate container. This is how we get the independence of database, worker and api. This gives us greater modularity and more convenient customization options