from app.db.session import SessionLocal
from app.db import crud
from app.models.database import ChatSession

db = SessionLocal()
session = db.query(ChatSession).first()
if session:
    print('Session:', session.session_id)
    history = crud.get_raw_chat_history(db, session.session_id)
    for msg in history:
        print(f"[{msg['role']}] {msg['content'][:50]}...")
else:
    print('No session found')
