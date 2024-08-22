import pytest
import os, sys, path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import User, Book, Borrowlist

# Test for adding a new user to the database
def test_add_user(db_session):
    # Create a new user instance
    new_user = User(username="test_user1", fullname="Test User One")
    db_session.add(new_user)
    db_session.commit()

    # Query the user to see if it is there
    user = db_session.query(User).filter_by(username="test_user1").first()
    assert user is not None
    assert user.username == "test_user1"
    assert user.fullname == "Test User One"

# Test for adding a new book to the database
def test_add_book(db_session):
    # Create a new book instance
    new_book = Book(title="Test Book Title", firstauthor="Author One", isbn="1234567890")
    db_session.add(new_book)
    db_session.commit()

    # Query the book to see if it is there
    book = db_session.query(Book).filter_by(isbn="1234567890").first()
    assert book is not None
    assert book.title == "Test Book Title"
    assert book.firstauthor == "Author One"

# Test for creating a borrow list entry
def test_create_borrowlist(db_session):
    # Add a user and a book
    user = User(username="test_user2", fullname="Test User Two")
    book = Book(title="Another Test Book", firstauthor="Author Two", isbn="0987654321")
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create a borrowlist entry
    borrow_entry = Borrowlist(user_id=user.id, book_id=book.id)
    db_session.add(borrow_entry)
    db_session.commit()

    # Query the borrowlist to ensure the entry is created
    borrowlist_entry = db_session.query(Borrowlist).filter_by(user_id=user.id).first()
    assert borrowlist_entry is not None
    assert borrowlist_entry.user_id == user.id
    assert borrowlist_entry.book_id == book.id

# Test for retrieving a user's borrowed books
def test_get_borrowlist(db_session):
    # Add a user and a book
    user = User(username="test_user3", fullname="Test User Three")
    book = Book(title="Yet Another Test Book", firstauthor="Author Three", isbn="1122334455")
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create a borrowlist entry
    borrow_entry = Borrowlist(user_id=user.id, book_id=book.id)
    db_session.add(borrow_entry)
    db_session.commit()

    # Query the borrowlist to retrieve the borrowed books
    borrowed_books = db_session.query(Borrowlist).filter_by(user_id=user.id).all()
    assert len(borrowed_books) == 1
    assert borrowed_books[0].book_id == book.id
    assert borrowed_books[0].user_id == user.id

# Test for deleting a user and cascading the deletion to their borrow list
def test_delete_user_cascade(db_session):
    # Add a user and a book
    user = User(username="test_user4", fullname="Test User Four")
    book = Book(title="Book for Deletion Test", firstauthor="Author Four", isbn="4455667788")
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create a borrowlist entry
    borrow_entry = Borrowlist(user_id=user.id, book_id=book.id)
    db_session.add(borrow_entry)
    db_session.commit()

    # Delete the user
    db_session.delete(user)
    db_session.commit()

    # Ensure the user is deleted
    deleted_user = db_session.query(User).filter_by(username="test_user4").first()
    assert deleted_user is None

    # Ensure the borrowlist entry for the deleted user is also removed
    deleted_borrow_entry = db_session.query(Borrowlist).filter_by(user_id=user.id).first()
    assert deleted_borrow_entry is None
