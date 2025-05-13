from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from models import Subscription
from database import SessionLocal
from datetime import datetime
import random
from email_utils import send_email
from zoneinfo import ZoneInfo

def fetch_new_fake_tweets(topic, already_sent_ids):
    """Simulates fetching new tweet IDs from a keyword search."""
    all_fake_ids = [f"{topic}_tweet_{random.randint(1000, 9999)}" for _ in range(3)]
    return [tid for tid in all_fake_ids if tid not in already_sent_ids]

def scheduled_job():
    db: Session = SessionLocal()
    subs = db.query(Subscription).all()
    now = datetime.now(ZoneInfo("America/New_York"))

    for sub in subs:
        last_sent = sub.last_sent.replace(tzinfo=ZoneInfo("America/New_York"))
        if (now - last_sent).total_seconds() >= sub.interval_minutes * 60:
            already_sent = sub.sent_ids.split(',') if sub.sent_ids else []
            new_ids = fetch_new_fake_tweets(sub.topic, already_sent)
            if new_ids:
                email_body = "\n".join([f"New tweet: {tid}" for tid in new_ids])
                send_email(
                    subject=f"Update on '{sub.topic}'",
                    body=email_body,
                    sender="your_email@gmail.com",
                    recipients=[sub.email],
                )
                sub.sent_ids = ','.join(already_sent + new_ids)
                sub.last_sent = now
                db.commit()

    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'interval', minutes=1)
    scheduler.start()
