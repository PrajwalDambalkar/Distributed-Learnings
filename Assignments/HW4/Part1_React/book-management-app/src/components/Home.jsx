import React from 'react';
import { useNavigate } from 'react-router-dom';

function Home({ books }) {
  const navigate = useNavigate();

  return (
    <>
      {/* Hero Section */}
      <header className="hero">
        <div className="hero-inner">
          <h1 className="heading">Book Management System</h1>
          <p className="subheading">Add, update, and manage your library!</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container">
        <section className="card">
          <h2 className="section-title">List of All Books</h2>

          {books.length === 0 ? (
            <div className="table-container">
              <table className="books-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Year</th>
                    <th>Genre</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td colSpan="5" className="empty-state">
                      No books in your library yet
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          ) : (
            <div className="table-container">
              <table className="books-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Year</th>
                    <th>Genre</th>
                  </tr>
                </thead>
                <tbody>
                  {books.map((book) => (
                    <tr key={book.id}>
                      <td>{book.id}</td>
                      <td>{book.title}</td>
                      <td>{book.author}</td>
                      <td>{book.year}</td>
                      <td>{book.genre}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Action Buttons */}
          <div className="actions-container">
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/create')}
            >
              Add Book
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/update')}
            >
              Update Book
            </button>
            <button 
              className="btn btn-danger"
              onClick={() => navigate('/delete')}
            >
              Delete Book
            </button>
          </div>
        </section>
      </main>
    </>
  );
}

export default Home;