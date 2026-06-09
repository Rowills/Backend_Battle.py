from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)#engine — the actual connection to your PostgreSQL database. It reads the URL from your .env

SessionLocal = sessionmaker(    #engine — the actual connection to your PostgreSQL database. It reads the URL from your .env
    autocommit = False,  # don't save anything automatically, wait for us to say so
    autoflush=False,  # don't send queries automatically
    bind=engine  
)

def get_db():    # a helper function that opens a DB session, gives it to a route, then closes it cleanly when done. 
    #This is used in every route that needs the database
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()