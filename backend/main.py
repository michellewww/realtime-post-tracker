from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.post("/api/search")
async def search_topics(request: SearchRequest):
    # Your existing search code remains the same
    keywords = re.findall(r'\w+', request.query.lower())
    unique_keywords = list(set(keywords))
    
    common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    filtered_keywords = [word for word in unique_keywords if word not in common_words and len(word) > 2]
    
    return {"keywords": filtered_keywords}

@app.post("/api/subscribe")
async def subscribe(email: str = Form(), topic: str = Form()):
    try:
        # Send confirmation email
        subject = f"Subscription Confirmation: {topic}"
        body = f"You have successfully subscribed to updates on '{topic}'. We'll send you notifications when new content is available."
        sender = "michellewangjm@gmail.com"
        recipients = [email]
        
        send_email(subject, body, sender, recipients)
        return {"status": "success", "message": f"Successfully subscribed {email} to updates on '{topic}'"}
    except Exception as e:
        print(f"Subscribe error: {e}")  # Add this for debugging
        raise HTTPException(status_code=500, detail=str(e))

def get_gmail_service():
    """Get an authorized Gmail API service instance."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(open('token.json').read()), SCOPES)
        except:
            # If token.json is invalid, we'll create a new one
            pass
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def send_email(subject, body, sender, recipients):
    """Send an email using the Gmail API."""
    try:
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = ', '.join(recipients)
        
        # Encode the message
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        
        # Send the message
        message = service.users().messages().send(
            userId='me', body={'raw': raw}).execute()
        
        print(f"Email sent successfully to {recipients} with message ID: {message['id']}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
