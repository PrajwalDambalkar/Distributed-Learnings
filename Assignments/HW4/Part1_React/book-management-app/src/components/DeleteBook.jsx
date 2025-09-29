import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function DeleteBook({ books, deleteBook }) {
  const navigate = useNavigate();
  const [bookId, setBookId] = useState('');
  const [bookToDelete, setBookToDelete] = useState(null);

  const handleIdChange = (e) => {
    const id = e.target.value;
    setBookId(id);
    
    if (id) {
      const book = books.find(b => b.id === parseInt(id));
      setBookToDelete(book || null);
    } else {
      setBookToDelete(null);
    }
  };

  const handleDelete = () => {
    if (!bookToDelete) {
      alert('Book not found!');
      return;
    }
    
    deleteBook(bookToDelete.id);
    navigate('/');
  };

  return (
    <>
      {/* Hero Section */}
      <header className="hero">
        <div className="hero-inner">
          <h1 className="heading">Delete Book</h1>
          <p className="subheading">Enter the Book ID to delete.</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container">
        <div className="form-container">
          <div className="warning-message">
            <h3>⚠ Warning</h3>
            <p>This action cannot be undone. Continue?</p>
          </div>

          <div className="form-group">
            <label htmlFor="bookId" className="form-label">Book ID</label>
            <input
              type="number"
              className="form-control"
              id="bookId"
              placeholder="Enter Book ID to delete"
              value={bookId}
              onChange={handleIdChange}
              autoComplete="off"
            />
            <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem' }}>
              Enter the ID of the book you want to delete
            </small>
          </div>

          {bookToDelete && (
            <div className="card" style={{ padding: '1.5rem', marginTop: '1.5rem', marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem', color: '#0f172a' }}>{bookToDelete.title}</h3>
              <p style={{ margin: '0.5rem 0', color: '#475569' }}>
                <strong>Author:</strong> {bookToDelete.author}
              </p>
              <p style={{ margin: '0.5rem 0', color: '#475569' }}>
                <strong>Year:</strong> {bookToDelete.year}
              </p>
              <p style={{ margin: '0.5rem 0', color: '#475569' }}>
                <strong>Genre:</strong> {bookToDelete.genre}
              </p>
            </div>
          )}

          <div className="form-actions">
            <button 
              className="btn btn-danger"
              onClick={handleDelete}
              disabled={!bookToDelete}
            >
              Delete Book
            </button>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => navigate('/')}
            >
              Cancel
            </button>
          </div>
        </div>
      </main>
    </>
  );
}

export default DeleteBook;