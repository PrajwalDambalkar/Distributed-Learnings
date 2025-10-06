import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updateBook, clearMessages } from '../store/booksSlice';

function UpdateBook() {
  const dispatch = useDispatch();
  const { loading, error, success } = useSelector((state) => state.books);

  const [bookId, setBookId] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    isbn: '',
    publication_year: '',
    available_copies: '',
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

    // Only send non-empty fields
    const bookData = {};
    if (formData.title) bookData.title = formData.title;
    if (formData.isbn) bookData.isbn = formData.isbn;
    if (formData.publication_year) bookData.publication_year = parseInt(formData.publication_year);
    if (formData.available_copies) bookData.available_copies = parseInt(formData.available_copies);
    if (formData.author_id) bookData.author_id = parseInt(formData.author_id);

    dispatch(updateBook({ id: parseInt(bookId), bookData }));

    // Clear form
    setFormData({
      title: '',
      isbn: '',
      publication_year: '',
      available_copies: '',
      author_id: '',
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Update Book</h1>

      {loading && <p>Updating book...</p>}
      {error && <p style={{ color: 'red' }}>Error: {JSON.stringify(error)}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}

      <form onSubmit={handleSubmit} style={{ maxWidth: '400px' }}>
        <div style={{ marginBottom: '10px' }}>
          <label>Book ID to Update:</label>
          <input
            type="number"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <hr />
        <p style={{ fontSize: '12px', color: 'gray' }}>
          Fill only the fields you want to update
        </p>

        <div style={{ marginBottom: '10px' }}>
          <label>Title:</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>ISBN:</label>
          <input
            type="text"
            name="isbn"
            value={formData.isbn}
            onChange={handleChange}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>Publication Year:</label>
          <input
            type="number"
            name="publication_year"
            value={formData.publication_year}
            onChange={handleChange}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>Available Copies:</label>
          <input
            type="number"
            name="available_copies"
            value={formData.available_copies}
            onChange={handleChange}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>Author ID:</label>
          <input
            type="number"
            name="author_id"
            value={formData.author_id}
            onChange={handleChange}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: 'blue', 
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Update Book
        </button>
      </form>
    </div>
  );
}

export default UpdateBook;