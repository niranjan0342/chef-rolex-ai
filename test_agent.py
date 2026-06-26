from app.services.agent import chef_agent
from app.db.session import SessionLocal

db = SessionLocal()
session_id = "test_memory_session_1"

# Chat 1
print("User: My name is Alice.")
res1 = chef_agent.chat(db, "My name is Alice.", session_id)
print("AI:", res1)

# Chat 2
print("User: What is my name?")
res2 = chef_agent.chat(db, "What is my name?", session_id)
print("AI:", res2)
