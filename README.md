# GT Chat API

## Table of Contents
- [Setup and Installation](#setup-and-installation)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Containers](#containers)

The project uses Alembic for database migration management, enabling version control and consistent updates to the database schema. 

Sensitive configuration data such as database credentials and RabbitMQ settings are stored in a `.env` file, which is excluded from version control to protect sensitive information

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
   
2. To run the project, create a `.env` file in the root directory with the following sample content:

    ```plaintext
    POSTGRES_USER=postgres_user
    POSTGRES_PASSWORD=password
    POSTGRES_PORT=5432
    POSTGRES_DB=tasks_db
    
    RABBITMQ_DEFAULT_USER=guest
    RABBITMQ_DEFAULT_PASS=guest_password
    RABBITMQ_PORT=5672
    ``` 
    - These environment variables configure the PostgreSQL and RabbitMQ connections required for the application.
   

3. **Build and Start Containers**: Run the following command to build and start the services:
   ```bash
   docker-compose up --build
   ```
4. **Stop the Application**: To stop the containers, run:
   ```bash
   docker-compose down
   ```

The application will be available at http://localhost:8000/docs

### Scaling Workers

To improve the speed of task processing from RabbitMQ, you can increase the number of worker containers. This can be achieved with the following command:

```bash
docker-compose up -d --scale worker=3
```

Increasing the number of worker containers can help manage a larger volume of tasks more efficiently, providing greater concurrency in task processing.

---

This project structure and configuration setup allow for modular development, scalable worker management, and efficient handling of background tasks, making it adaptable to various production environments.


## Project Structure

```
gt_chat/
├── alembic/                                # Directory for Alembic migration files
│   ├── versions/                           # Folder for storing migration files
│   ├── env.py                              # Alembic setup for integration with SQLAlchemy
│   ├── README                              # Information on Alembic usage
├── app/
│   ├── __init__.py
│   ├── main.py                             # FastAPI entry point
│   ├── db.py                               # PostgreSQL database connection setup
│   ├── crud.py                             # CRUD functions for database interactions
│   ├── schemas.py                          # Pydantic models for data validation
│   ├── message_queue.py                    # RabbitMQ configuration
│   ├── models.py                           # SQLAlchemy database models
│   └── config.py                           # Configuration file for application settings
├── worker_app/
│   ├── __init__.py
│   ├── worker.py                           # Main worker script for message processing
│   └── process_task.py                     # Text task processing module
├── tests/
│   ├── __init__.py
│   ├── test_api.py                         # Tests for FastAPI endpoints
│   └── test_worker.py                      # Tests for worker functions
├── shared_data/                            # Shared storage for any required files
├── alembic.ini                             # Alembic configuration file
├── Dockerfile_api                          # Dockerfile for FastAPI service
├── Dockerfile_worker                       # Dockerfile for worker service
├── docker-compose.yml                      # Docker Compose file for running services
├── .env                                    # Environment variables file (included in .gitignore)
├── requirements.txt                        # Dependencies for FastAPI
├── requirements_worker.txt                 # Dependencies for the worker service
└── README.md                               # Project description
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
For additional data backup, data is saved in the database before sending to the queue. This allows you to track tasks that have not been processed

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
- `test_word_count`: Ensures accurate word counting in cleaned text.
- `test_process_task`: Tests task processing, including cleaning text, detecting language, and counting words.
- `test_connect_to_rabbitmq_success`: Confirms successful connection to RabbitMQ, validating that a connection is established.
- `test_connect_to_rabbitmq_failure`: Simulates RabbitMQ connection failure, checking retries and final fallback behavior.

## Containers
This project includes the following Docker containers:
- **`fastapi_app`**: Hosts the FastAPI application, exposing endpoints for processing and retrieving text data.
- **`rabbitmq`**: Provides the RabbitMQ message broker for task queuing.
- **`worker`**: Worker service that consumes messages from RabbitMQ, processes the text, and updates the database with results.
- **`postgres_db`**: A dedicated PostgreSQL database container, `postgres_db`, has been created to ensure modularity and data management consistency. This container checks for database availability every 10 seconds, helping maintain connection stability across services. PostgreSQL is used to ensure a reliable and scalable storage solution for task data.
