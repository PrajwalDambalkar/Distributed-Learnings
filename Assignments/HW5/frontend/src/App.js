import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import CreateBook from './components/CreateBook';
import UpdateBook from './components/UpdateBook';

function App() {
  return (
    <Router>
      <div>
        <nav style={{ backgroundColor: '#333', padding: '10px' }}>
          <Link to="/" style={{ color: 'white', margin: '0 10px', textDecoration: 'none' }}>
            Home
          </Link>
          <Link to="/create" style={{ color: 'white', margin: '0 10px', textDecoration: 'none' }}>
            Create Book
          </Link>
          <Link to="/update" style={{ color: 'white', margin: '0 10px', textDecoration: 'none' }}>
            Update Book
          </Link>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create" element={<CreateBook />} />
          <Route path="/update" element={<UpdateBook />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;