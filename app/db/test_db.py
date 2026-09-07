"""Manual smoke test that prints whether the configured database is reachable."""

from app.db.database import engine


try:
    with engine.connect() as connection:
        print("Database connection successful!")

except Exception as e:
    print("Database connection failed:")
    print(e)
