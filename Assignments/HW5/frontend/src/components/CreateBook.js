import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createBook, clearMessages } from '../store/booksSlice';
import '../styles.css';

function CreateBook() {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.books);

  const [formData, setFormData] = useState({
    title: '',
    isbn: '',
    publication_year: '',
    available_copies: 1,
    author_id: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(clearMessages());
    
    const bookData = {
      ...formData,
      publication_year: parseInt(formData.publication_year),
      available_copies: parseInt(formData.available_copies),
      author_id: parseInt(formData.author_id),
    };

    dispatch(createBook(bookData));
    
    setFormData({
      title: '',
      isbn: '',
      publication_year: '',
      available_copies: 1,
      author_id: '',
    });
  };

  return (
    <div className="container">
      <h1>Create New Book</h1>

      {loading && <p className="loading">Creating book...</p>}
      {error && <div className="alert alert-error">Error: {JSON.stringify(error)}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title:</label>
          <input type="text" name="title" value={formData.title} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>ISBN:</label>
          <input type="text" name="isbn" value={formData.isbn} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Publication Year:</label>
          <input type="number" name="publication_year" value={formData.publication_year} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Available Copies:</label>
          <input type="number" name="available_copies" value={formData.available_copies} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Author ID:</label>
          <input type="number" name="author_id" value={formData.author_id} onChange={handleChange} required />
        </div>

        <button type="submit" disabled={loading} className="create-btn">
          Create Book
        </button>
      </form>
    </div>
  );
}

export default CreateBook;