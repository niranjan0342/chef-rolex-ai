from app.db.session import SessionLocal
from app.models.database import Message

db = SessionLocal()
msgs = db.query(Message).order_by(Message.created_at.desc()).limit(20).all()
msgs.reverse()

for m in msgs:
    print(f"[{m.created_at.strftime('%H:%M:%S')}] [{m.session_id[-4:]}] {m.role}: {m.content[:50]}")
