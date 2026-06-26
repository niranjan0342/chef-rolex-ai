from app.services.agent import chef_agent
from app.db.session import SessionLocal

db = SessionLocal()
session_id = "test_stream_session_1"

# Chat 1
print("User: My name is Alice.")
res1 = ""
for chunk in chef_agent.chat_stream(db, "My name is Alice.", session_id):
    res1 += chunk
print("AI:", res1)

# Chat 2
print("User: What is my name?")
res2 = ""
for chunk in chef_agent.chat_stream(db, "What is my name?", session_id):
    res2 += chunk
print("AI:", res2)
