import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBooks, deleteBook } from '../store/booksSlice';
import '../styles.css';

function Home() {
  const dispatch = useDispatch();
  const { books, loading, error, success } = useSelector((state) => state.books);

  useEffect(() => {
    dispatch(fetchBooks());
  }, [dispatch]);

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this book?')) {
      dispatch(deleteBook(id));
    }
  };

  return (
    <div className="container">
      <h1>Library Books</h1>
      
      {loading && <p className="loading">Loading...</p>}
      {error && <div className="alert alert-error">Error: {JSON.stringify(error)}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>ISBN</th>
            <th>Year</th>
            <th>Copies</th>
            <th>Author ID</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.id}>
              <td>{book.id}</td>
              <td>{book.title}</td>
              <td>{book.isbn}</td>
              <td>{book.publication_year}</td>
              <td>{book.available_copies}</td>
              <td>{book.author_id}</td>
              <td>
                <button className="delete-btn" onClick={() => handleDelete(book.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {books.length === 0 && !loading && <p>No books found.</p>}
    </div>
  );
}

export default Home;