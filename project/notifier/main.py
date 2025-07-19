import asyncio
import aiohttp
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Notification Service", version="1.0.0")

class NotificationRequest(BaseModel):
    type: str  # 'anomaly', 'device_offline', 'system_alert'
    device_id: str
    message: str
    severity: str = 'medium'
    email_recipients: Optional[list] = None

# Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

async def send_slack_notification(message: str, severity: str):
    """Send notification to Slack"""
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL not configured")
        return False
    
    color_map = {
        'high': '#ff0000',
        'medium': '#ffaa00',
        'low': '#00ff00'
    }
    
    payload = {
        "attachments": [
            {
                "color": color_map.get(severity, '#808080'),
                "title": "VigilanceOS Alert",
                "text": message,
                "footer": "VigilanceOS Monitoring",
                "ts": int(asyncio.get_event_loop().time())
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SLACK_WEBHOOK_URL, json=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")
        return False

async def send_email_notification(message: str, recipients: list, subject: str):
    """Send email notification"""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("Email credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Add body
        body = f"""
        VigilanceOS Alert
        
        {message}
        
        ---
        This is an automated message from VigilanceOS Monitoring System.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, recipients, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Notification Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "slack_configured": bool(SLACK_WEBHOOK_URL),
        "email_configured": bool(EMAIL_USERNAME and EMAIL_PASSWORD)
    }

@app.post("/notify")
async def send_notification(request: NotificationRequest):
    """Send notification via configured channels"""
    results = {}
    
    # Format message
    formatted_message = f"Device: {request.device_id}\nSeverity: {request.severity}\nMessage: {request.message}"
    
    # Send Slack notification
    if SLACK_WEBHOOK_URL:
        slack_result = await send_slack_notification(formatted_message, request.severity)
        results['slack'] = slack_result
    
    # Send email notification
    if request.email_recipients and EMAIL_USERNAME:
        subject = f"VigilanceOS Alert - {request.type.title()} ({request.severity.title()})"
        email_result = await send_email_notification(
            formatted_message, 
            request.email_recipients, 
            subject
        )
        results['email'] = email_result
    
    return {
        "message": "Notification sent",
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)