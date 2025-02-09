# Task Management System

## Overview

This project is a Task Management System built with FastAPI. It includes features for creating, updating, deleting, and viewing tasks, as well as generating task summaries for employees.

## Prerequisites

- Docker
- Docker Compose

## Running the Application

1. **Clone the repository:**

    ```sh
    git clone git@github.com:khanhduy14/knovel-assessment.git
    cd knovel-assessment
    ```

2. **Create and configure environment variables:**

    Create a `.env` file in the root directory and add the following environment variables:

    ```env
    WEBSERVER_HOST=0.0.0.0
    WEBSERVER_PORT=8080
    DB_CONNECTION_STRING=postgresql://postgres:postgres@db:5432/taskdb
    JWT_SECRET_KEY=zkX2jO9lLMPavt2pf4AiC8C3eUK64F_zqL7Q1XsVH9o
    JWT_ALGORITHM=HS256
    JWT_TOKEN_EXPIRE_MINS=30
    ```

3. **Build and run the Docker containers:**

    ```sh
    docker-compose up --build
    ```

4. **Access the application:**

    The application will be available at `http://localhost:8080`.

## Stopping the Application

To stop the application, run:

```sh
docker-compose down
```

## Sample Flow

1. **Login as Employer**

    ```sh
    curl -X POST "http://localhost:8080/v1/users/login" -H "Content-Type: application/json" -d '{
        "username": "test-employer",
        "password": "test-employer"
    }'
    ```

    Response:
    ```json
    {
        "access_token": "employer_token",
        "token_type": "bearer"
    }
    ```

2. **Create Task**

    ```sh
    curl -X POST "http://localhost:8080/v1/tasks" -H "Authorization: Bearer employer_token" -H "Content-Type: application/json" -d '{
        "title": "Sample Task",
        "description": "This is a sample task",
        "due_date": "2023-12-31T23:59:59",
        "assignee_id": "employee_uuid"
    }'
    ```

    Response:
    ```json
    {
        "id": "task_uuid",
        "title": "Sample Task",
        "description": "This is a sample task",
        "status": "Pending",
        "created_at": "2023-10-01T12:00:00",
        "due_date": "2023-12-31T23:59:59",
        "assignee_id": "employee_uuid",
        "creator_id": "employer_uuid"
    }
    ```

3. **Employer Get Tasks**

    ```sh
    curl -X GET "http://localhost:8080/v1/tasks" -H "Authorization: Bearer employer_token"
    ```

    Response:
    ```json
    [
        {
            "id": "task_uuid",
            "title": "Sample Task",
            "description": "This is a sample task",
            "status": "Pending",
            "created_at": "2023-10-01T12:00:00",
            "due_date": "2023-12-31T23:59:59",
            "assignee_id": "employee_uuid",
            "creator_id": "employer_uuid"
        }
    ]
    ```

4. **Login as Employee**

    ```sh
    curl -X POST "http://localhost:8080/v1/users/login" -H "Content-Type: application/json" -d '{
        "username": "test-employee",
        "password": "test-employee"
    }'
    ```

    Response:
    ```json
    {
        "access_token": "employee_token",
        "token_type": "bearer"
    }
    ```

5. **Employee Get List of Their Tasks**

    ```sh
    curl -X GET "http://localhost:8080/v1/tasks/my-tasks" -H "Authorization: Bearer employee_token"
    ```

    Response:
    ```json
    [
        {
            "id": "task_uuid",
            "title": "Sample Task",
            "description": "This is a sample task",
            "status": "Pending",
            "created_at": "2023-10-01T12:00:00",
            "due_date": "2023-12-31T23:59:59",
            "assignee_id": "employee_uuid",
            "creator_id": "employer_uuid"
        }
    ]
    ```

6. **Employer Get Task Summary**

    ```sh
    curl -X GET "http://localhost:8080/v1/tasks/task-summary" -H "Authorization: Bearer employer_token"
    ```

    Response:
    ```json
    [
        {
            "employee_id": "employee_uuid",
            "username": "test-employee",
            "total_tasks": 1,
            "completed_tasks": 0
        }
    ]
    ```

7 (Optional). **Create an user**

    ```sh
    #Create an employee
    curl -X POST "http://localhost:8080/v1/users" -H "Content-Type: application/json" -d '{
        "username": "test-employee",
        "password": "test-employee",
        "role": "Employee"
    }'

    #Create an employer
    curl -X POST "http://localhost:8080/v1/users" -H "Content-Type: application/json" -d '{
        "username": "test-employer",
        "password": "test-employer",
        "role": "Employer"
    }'
    ```