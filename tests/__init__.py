# tests/__init__.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from sqlalchemy import text

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


Session = sessionmaker(bind=engine)

# function to check if the database connection is working
def test_db_connection():
    try:
        # Attempt to create a session and execute a simple query
        session = Session()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        # Print the error if the connection test fails
        print(f"Database connection test failed: {e}")
        return False


db_connection_status = test_db_connection()
print(f"Database connection test: {'Success' if db_connection_status else 'Failure'}")
