# Email Management System

## Overview
This project is an Email Management System designed to handle over 100,000 emails, including reading, replying, and managing spam/promotions while maintaining IP reputation. It integrates:
- **FastAPI** for the backend API.
- **Celery** for asynchronous task processing.
- **PostgreSQL** for database management.
- **Redis** as a message broker for Celery.
- **Gmail API** for email operations.

---

## Prerequisites
1. **Docker** and **Docker Compose** installed.
2. Google Cloud project with Gmail API enabled.
3. PostgreSQL and Redis set up (via Docker Compose).
4. Python (for manual debugging and Gmail token generation).

---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd email-management-system
```

### Step 2: Create the `.env` File
1. Create a `.env` file in the root directory:
   ```bash
   echo "DATABASE_URL=postgresql://user:password@localhost/email_db\nREDIS_URL=redis://localhost:6379/0" > .env
   ```
2. Ensure the `.env` file contains the following environment variables:
   ```plaintext
   DATABASE_URL=postgresql://user:password@localhost/email_db
   REDIS_URL=redis://localhost:6379/0
   ```

### Step 3: Set Up Google Cloud Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a new project**:
   - Navigate to the project selector dropdown and click "New Project."
   - Provide a project name (e.g., `EmailManager`) and click "Create."
3. **Enable Gmail API**:
   - In the "APIs & Services" section, click "Enable APIs and Services."
   - Search for and enable the Gmail API.
4. **Create OAuth 2.0 Credentials**:
   - Go to "Credentials" and click "Create Credentials > OAuth 2.0 Client IDs."
   - Download the `credentials.json` file and place it in the project root.

### Step 4: Build and Run the Application
1. Build the Docker containers:
   ```bash
   docker-compose up --build
   ```
2. The API will be accessible at `http://localhost:8000`.

---

## Testing the Endpoints

### Test Gmail API Connectivity
Add the following endpoint to `main.py`:
```python
@app.get("/test-gmail")
def test_gmail():
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId='me').execute()
        return {"status": "Success", "labels": results.get('labels', [])}
    except Exception as e:
        return {"error": str(e)}
```
Then, test the endpoint:
```bash
curl -X GET http://localhost:8000/test-gmail
```

### Test Database Connectivity
Add the following endpoint to `main.py`:
```python
@app.get("/test-db")
def test_db():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "Database Connected"}
    except Exception as e:
        return {"error": str(e)}
```
Call the endpoint:
```bash
curl -X GET http://localhost:8000/test-db
```

---

## Debugging Common Issues

### Error: `Internal Server Error`
#### Cause 1: Missing or Invalid `credentials.json`
- Ensure the file is in the root directory and correctly configured.

#### Cause 2: Database Connection Issues
- Check database logs:
  ```bash
  docker-compose logs db
  ```
- Verify that `DATABASE_URL` is correct in `.env`.

#### Cause 3: Redis Connection Issues
- Check Redis logs:
  ```bash
  docker-compose logs redis
  ```

### Viewing Logs
To view logs for all services:
```bash
docker-compose logs
```

---

## Folder Structure
```
email-management-system/
|-- main.py
|-- Dockerfile
|-- requirements.txt
|-- docker-compose.yaml
|-- .env
|-- credentials.json
```

---

## Endpoints
### Fetch Emails
**GET** `/emails`
- Fetches emails from Gmail and stores them in the database.

### Reply to Email
**POST** `/reply/{email_id}`
- Schedules a task to reply to a specific email.

---

## Deployment
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the API at `http://localhost:8000`.
3. Use tools like Postman or `curl` to test endpoints.

---

## Future Enhancements
- Add Microsoft API support.
- Implement advanced email categorization (spam, promotions).
- Monitor and maintain IP reputation automatically.


