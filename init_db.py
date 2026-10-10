from app.core.database import engine, Base
from app.models.habit import  Habit

def create_tables():
    print("Connecting to SQLite and building tables...")
    # Inspects all subclasses of Base and emits CREATE TABLE IF NOT EXISTS
    Base.metadata.create_all(bind=engine)
    print("Success: 'mindforge.db' has been created with the 'habits' table!")

if __name__ == "__main__":
    create_tables()