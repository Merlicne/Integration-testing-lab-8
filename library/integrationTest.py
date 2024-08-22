import pytest
from fastapi.testclient import TestClient

import os, sys, path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import app, get_db, User, Book, Borrowlist

# Create a test client to interact with the API
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.mark.parametrize("username, fullname", [
    ("test_user1", "Test User One"),
    ("test_user2", "Test User Two"),
    ("test_user3", "Test User Three")
])
def test_create_user(client, db_session, username, fullname):
    # Make a POST request to the /users/ endpoint with query parameters
    response = client.post(f"/users/?username={username}&fullname={fullname}")

    # Check that the API request was successful
    assert response.status_code == 200

    # Check that the user returned by the API matches the one we sent
    assert response.json()["username"] == username
    assert response.json()["fullname"] == fullname

    # Check that the user was successfully added to the database
    assert db_session.query(User).filter_by(username=username).first()

@pytest.mark.parametrize("title, firstauthor, isbn", [
    ("Test Book Title 1", "Author One", "1234567890"),
    ("Test Book Title 2", "Author Two", "0987654321"),
    ("Test Book Title 3", "Author Three", "1122334455")
])
def test_create_book(client, db_session, title, firstauthor, isbn):
    # Make a POST request to the /books/ endpoint with query parameters
    response = client.post(f"/books/?title={title}&firstauthor={firstauthor}&isbn={isbn}")

    # Check that the API request was successful
    assert response.status_code == 200

    # Check that the book returned by the API matches the one we sent
    assert response.json()["title"] == title
    assert response.json()["firstauthor"] == firstauthor
    assert response.json()["isbn"] == isbn

    # Check that the book was successfully added to the database
    assert db_session.query(Book).filter_by(isbn=isbn).first()

def test_create_borrowlist(client, db_session):
    # Add a user and a book to the database
    user = User(username="test_user4", fullname="Test User Four")
    book = Book(title="Test Book for Borrowing", firstauthor="Author Four", isbn="4455667788")
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Make a POST request to the /borrowlist/ endpoint with query parameters
    response = client.post(f"/borrowlist/?user_id={user.id}&book_id={book.id}")

    # Check that the API request was successful
    assert response.status_code == 200

    # Check that the borrowlist entry returned by the API matches the one we sent
    assert response.json()["user_id"] == user.id
    assert response.json()["book_id"] == book.id

    # Check that the borrowlist entry was successfully added to the database
    assert db_session.query(Borrowlist).filter_by(user_id=user.id, book_id=book.id).first()

def test_get_borrowlist(client, db_session):
    # Add a user and a book, and create a borrowlist entry
    user = User(username="test_user5", fullname="Test User Five")
    book = Book(title="Another Test Book", firstauthor="Author Five", isbn="5566778899")
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    borrow_entry = Borrowlist(user_id=user.id, book_id=book.id)
    db_session.add(borrow_entry)
    db_session.commit()

    # Make a GET request to the /borrowlist/{user_id} endpoint
    response = client.get(f"/borrowlist/{user.id}")

    # Check that the API request was successful
    assert response.status_code == 200

    # Check that the borrowlist entry matches the expected result
    borrowlist = response.json()[0]
    assert borrowlist["user_id"] == user.id
    assert borrowlist["book_id"] == book.id

def test_get_borrowlist_no_entries(client, db_session):
    # Add a user with no borrow entries
    user = User(username="test_user6", fullname="Test User Six")
    db_session.add(user)
    db_session.commit()

    # Make a GET request to the /borrowlist/{user_id} endpoint
    response = client.get(f"/borrowlist/{user.id}")

    # Check that the API request returns a 404 not found
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found or no book being borrowed by the user"
