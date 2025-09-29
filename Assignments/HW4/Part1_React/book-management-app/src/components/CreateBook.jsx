import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function CreateBook({ addBook }) {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
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
    
    const bookData = {
      ...formData,
      year: parseInt(formData.year)
    };
    
    addBook(bookData);
    navigate('/');
  };

  return (
    <>
      {/* Hero Section */}
      <header className="hero">
        <div className="hero-inner">
          <h1 className="heading">Add a New Book</h1>
          <p className="subheading">Enter the title and author, then save.</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container">
        <div className="form-container">
          <form onSubmit={handleSubmit} className="book-form">
            <div className="form-group">
              <label htmlFor="title" className="form-label">Title</label>
              <input
                type="text"
                className="form-control"
                id="title"
                name="title"
                placeholder="Type Book Title"
                value={formData.title}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="author" className="form-label">Author</label>
              <input
                type="text"
                className="form-control"
                id="author"
                name="author"
                placeholder="Type Author Name"
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
                placeholder="Enter Year"
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
                placeholder="Enter Genre"
                value={formData.genre}
                onChange={handleChange}
                required
                autoComplete="off"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Add Book
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

export default CreateBook;