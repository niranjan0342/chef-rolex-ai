import requests
from sqlalchemy import create_engine, text
from app.db import crud
from app.db.session import SessionLocal

engine = create_engine("postgresql://postgres:Nira_66@localhost:5432/chef_rolex_db")

with SessionLocal() as db:
    sessions = db.execute(text("SELECT session_id FROM sessions WHERE title='New Chat'")).fetchall()
    
    for row in sessions:
        s_id = row[0]
        # get first message
        history = crud.get_chat_history(db, s_id, 100)
        first_msg = None
        for m in history:
            if m.type == "human":
                first_msg = m.content
                break
        
        if first_msg:
            try:
                from app.services.agent import chef_agent
                title = chef_agent.title_chain.invoke({"input": first_msg}).strip('" \n')
                crud.update_session_title(db, s_id, title)
                print(f"Updated {s_id} -> {title}")
            except Exception as e:
                print(e)
