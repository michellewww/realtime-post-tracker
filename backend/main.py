from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

class SubscriptionRequest(BaseModel):
    email: EmailStr
    topic: str

@app.post("/api/search")
async def search_topics(request: SearchRequest):
    # Extract keywords from the query
    # This is a simple implementation; you might want to use NLP for better extraction
    keywords = re.findall(r'\w+', request.query.lower())
    unique_keywords = list(set(keywords))
    
    # Filter out common words (optional)
    common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    filtered_keywords = [word for word in unique_keywords if word not in common_words and len(word) > 2]
    
    return {"keywords": filtered_keywords}

@app.post("/api/subscribe")
async def subscribe(email: str = Form(...), topic: str = Form(...)):
    try:
        # In a real app, you would save this to a database
        # Here we'll just send an email
        send_confirmation_email(email, topic)
        return {"status": "success", "message": f"Successfully subscribed {email} to updates on '{topic}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def send_confirmation_email(to_email, topic):
    # This is a placeholder for the actual email sending logic
    # You'll need to set up Google API credentials and store them securely
    
    # In a real implementation, you would:
    # 1. Load credentials from environment variables or secure storage
    # 2. Create a Gmail API client
    # 3. Compose and send the email
    
    # For now, we'll just print what would happen
    print(f"Would send confirmation email to {to_email} about topic '{topic}'")
    
    # Uncomment and complete this code when you have your Google API credentials
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    # Load credentials from service account file
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    
    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Create message
    message = MIMEText(f"You have successfully subscribed to updates on '{topic}'")
    message['to'] = to_email
    message['from'] = 'michellewangjm@gmail.com'
    message['subject'] = f'Subscription Confirmation: {topic}'
    
    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    # Send the message
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    """
    
    return True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
