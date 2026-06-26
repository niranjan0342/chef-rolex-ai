from app.db.session import engine, Base
from app.models.database import User, ChatSession, Message

# எல்லா tables-உம் create பண்ணு
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")