import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function UpdateBook({ books, updateBook }) {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    id: '',
    title: '',
    author: '',
    year: '',
    genre: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const bookId = parseInt(formData.id);
    const bookExists = books.find(book => book.id === bookId);
    
    if (!bookExists) {
      alert(`Book with ID ${bookId} not found!`);
      return;
    }
    
    const updatedData = {
      title: formData.title,
      author: formData.author,
      year: parseInt(formData.year),
      genre: formData.genre
    };
    
    updateBook(bookId, updatedData);
    navigate('/');
  };

  return (
    <>
      {/* Hero Section */}
      <header className="hero">
        <div className="hero-inner">
          <h1 className="heading">Update a Book</h1>
          <p className="subheading">Enter the Book ID and the new title/author, then save.</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container">
        <div className="form-container">
          <form onSubmit={handleSubmit} className="book-form">
            <div className="form-group">
              <label htmlFor="id" className="form-label">Book ID</label>
              <input
                type="number"
                className="form-control"
                id="id"
                name="id"
                placeholder="Enter Book ID"
                value={formData.id}
                onChange={handleChange}
                required
                autoComplete="off"
              />
              <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                Enter the ID of the book you want to update
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="title" className="form-label">New Title</label>
              <input
                type="text"
                className="form-control"
                id="title"
                name="title"
                placeholder="Enter new title"
                value={formData.title}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="author" className="form-label">New Author</label>
              <input
                type="text"
                className="form-control"
                id="author"
                name="author"
                placeholder="Enter new author"
                value={formData.author}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="year" className="form-label">Year</label>
              <input
                type="number"
                className="form-control"
                id="year"
                name="year"
                placeholder="Enter year"
                value={formData.year}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="genre" className="form-label">Genre</label>
              <input
                type="text"
                className="form-control"
                id="genre"
                name="genre"
                placeholder="Enter genre"
                value={formData.genre}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Update Book
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => navigate('/')}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}

export default UpdateBook;