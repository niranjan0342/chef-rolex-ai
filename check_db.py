from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:Nira_66@localhost:5432/chef_rolex_db")
with engine.connect() as conn:
    res = conn.execute(text("SELECT id, title FROM sessions"))
    for row in res:
        print(row)
