from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from celery import Celery
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# FastAPI Initialization
app = FastAPI()

# Celery Initialization
celery = Celery(__name__, broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/email_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Email Model
class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(String)
    replied = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Gmail Service Setup
def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        'credentials.json', ['https://www.googleapis.com/auth/gmail.readonly']
    )
    service = build('gmail', 'v1', credentials=creds)
    return service

# Fetch Emails Endpoint
@app.get("/emails")
def fetch_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    
    db = SessionLocal()
    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        db_email = Email(
            sender=message['payload']['headers'][0]['value'],
            subject=message['snippet'],
            body=message['snippet'],
        )
        db.add(db_email)
    db.commit()
    db.close()

    return JSONResponse(content={"status": "Emails Fetched"})

# Send Reply Task
@celery.task
def send_reply_task(email_id: int, reply_content: str):
    service = get_gmail_service()
    db = SessionLocal()
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise ValueError("Email not found")

    reply_message = {
        'raw': reply_content
    }
    service.users().messages().send(userId='me', body=reply_message).execute()

    email.replied = True
    db.commit()
    db.close()

# Reply Endpoint
@app.post("/reply/{email_id}")
def reply_email(email_id: int, reply_content: str):
    send_reply_task.delay(email_id, reply_content)
    return JSONResponse(content={"status": "Reply Scheduled"})
