import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys, path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import Base, SQLALCHEMY_DATABASE_URL

# Setup an in-memory SQLite database for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionTesting = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    session = SessionTesting()

    yield session

    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)
