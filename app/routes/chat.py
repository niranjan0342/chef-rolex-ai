from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import chef_agent
from app.db.session import get_db
from app.db import crud
import uuid
import json
from app.routes.auth import get_current_user_optional, get_current_user
from app.models.database import User

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user_optional)):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        session_id = request.session_id
        if not session_id or session_id.lower() == "null":
            session_id = str(uuid.uuid4())

        user_id = user.id if user else None



        response = chef_agent.chat(
            db=db,
            message=request.message,
            session_id=session_id,
            user_id=user_id,
            username=user.username if user else None
        )

        return ChatResponse(
            response=response,
            session_id=session_id,
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user_optional)):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        session_id = request.session_id
        if not session_id or session_id.lower() == "null":
            session_id = str(uuid.uuid4())

        user_id = user.id if user else None



        def generate():
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

            for chunk in chef_agent.chat_stream(db=db, message=request.message, session_id=session_id, user_id=user_id, username=user.username if user else None):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.delete("/chat/history/{session_id}")
async def clear_history(session_id: str, db: Session = Depends(get_db)):
    try:
        crud.delete_session_history(db, session_id)
        return {
            "message": f"History cleared for {session_id}",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{session_id}")
async def get_history(session_id: str, db: Session = Depends(get_db)):
    try:
        messages = crud.get_raw_chat_history(db, session_id)
        return {
            "session_id": session_id,
            "messages": messages,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        sessions = crud.get_user_sessions(db, user.id)
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))