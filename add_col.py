from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:Nira_66@localhost:5432/chef_rolex_db")
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS title VARCHAR(200) DEFAULT 'New Chat'"))
        conn.commit()
    print("Column added successfully.")
except Exception as e:
    print("Error:", e)
