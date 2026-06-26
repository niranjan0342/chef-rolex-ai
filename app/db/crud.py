from sqlalchemy.orm import Session
from app.models.database import User, ChatSession, Message
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# Session create பண்ணு (if not exists)
def get_or_create_session(db: Session, session_id: str, user_id: int = None):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()

    if not session:
        session = ChatSession(session_id=session_id, user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    return session

def update_session_title(db: Session, session_id: str, title: str):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if session:
        session.title = title
        db.commit()


# Message save பண்ணு
def save_message(db: Session, session_id: str, role: str, content: str):
    message = Message(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    return message


# History load பண்ணு (LangChain format-ல)
def get_chat_history(db: Session, session_id: str, limit: int = 10):
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()

    # Last N messages மட்டும்
    messages = messages[-limit:] if len(messages) > limit else messages

    # LangChain format-ஆ convert பண்ணு
    chat_history = []
    for msg in messages:
        if msg.role == "human":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))

    return chat_history


# History delete பண்ணு
def delete_session_history(db: Session, session_id: str):
    db.query(Message).filter(
        Message.session_id == session_id
    ).delete()
    db.commit()


# Raw History load பண்ணு (JSON format-ல)
def get_raw_chat_history(db: Session, session_id: str):
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return [{"role": msg.role, "content": msg.content} for msg in messages]

# User CRUD

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_sessions(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()