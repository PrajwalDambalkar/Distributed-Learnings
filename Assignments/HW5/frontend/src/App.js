import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import CreateBook from './components/CreateBook';
import UpdateBook from './components/UpdateBook';
import Chat from './components/Chat';

function App() {
  return (
    <Router>
      <div>
        <nav style={{ backgroundColor: '#667eea', padding: '15px 30px' }}>
          <Link to="/" style={{ color: 'white', margin: '0 15px', textDecoration: 'none', fontWeight: '500' }}>
            Home
          </Link>
          <Link to="/create" style={{ color: 'white', margin: '0 15px', textDecoration: 'none', fontWeight: '500' }}>
            Create Book
          </Link>
          <Link to="/update" style={{ color: 'white', margin: '0 15px', textDecoration: 'none', fontWeight: '500' }}>
            Update Book
          </Link>
          <Link to="/chat" style={{ color: 'white', margin: '0 15px', textDecoration: 'none', fontWeight: '500' }}>
            AI Chat
          </Link>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create" element={<CreateBook />} />
          <Route path="/update" element={<UpdateBook />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;