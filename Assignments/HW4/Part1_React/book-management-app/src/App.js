import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DarkModeToggle from './components/DarkModeToggle';
import Home from './components/Home';
import CreateBook from './components/CreateBook';
import UpdateBook from './components/UpdateBook';
import DeleteBook from './components/DeleteBook';
import './App.css';

function App() {
  // State to store books array
  const [books, setBooks] = useState([
    { id: 1, title: '1984', author: 'George Orwell', year: 1949, genre: 'Dystopian' },
    { id: 2, title: 'The Hobbit', author: 'J.R.R. Tolkien', year: 1937, genre: 'Fantasy' }
  ]);

  // State to store selected book for update/delete
  const [selectedBook, setSelectedBook] = useState(null);

  // Dark mode state
  const [darkMode, setDarkMode] = useState(false);

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  // Add new book function
  const addBook = (bookData) => {
    const newBook = {
      id: books.length > 0 ? Math.max(...books.map(b => b.id)) + 1 : 1,
      ...bookData
    };
    setBooks([...books, newBook]);
  };

  // Update book function
  const updateBook = (id, updatedData) => {
    setBooks(books.map(book => 
      book.id === id ? { ...book, ...updatedData } : book
    ));
  };

  // Delete book function
  const deleteBook = (id) => {
    setBooks(books.filter(book => book.id !== id));
  };

  return (
    <Router>
      <div className="App">
        <DarkModeToggle darkMode={darkMode} setDarkMode={setDarkMode} />
        <Routes>
          <Route 
            path="/" 
            element={
              <Home 
                books={books}
              />
            } 
          />
          <Route 
            path="/create" 
            element={<CreateBook addBook={addBook} />} 
          />
          <Route 
            path="/update" 
            element={
              <UpdateBook 
                books={books}
                updateBook={updateBook}
              />
            } 
          />
          <Route 
            path="/delete" 
            element={
              <DeleteBook 
                books={books}
                deleteBook={deleteBook}
              />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;