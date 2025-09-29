require('dotenv').config();
const express = require('express');
const { sequelize } = require('./models');
const bookRoutes = require('./routes/book.routes');

const app = express(); // Initialize Express app
const PORT = process.env.PORT || 3000; // Default port

// Middleware
app.use(express.json({ space: 2 })); // This adds formatting
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', bookRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({ 
    message: 'Book Management API',
    endpoints: {
      'GET /api/books': 'Get all books',
      'GET /api/books/:id': 'Get book by ID',
      'POST /api/books': 'Create new book',
      'PUT /api/books/:id': 'Update book',
      'DELETE /api/books/:id': 'Delete book'
    }
  });
});

// Test database connection and start server
async function startServer() {
  try {
    await sequelize.authenticate();
    console.log('Database connection established successfully.');
    
    app.listen(PORT, () => {
      console.log(`Server is running on http://localhost:${PORT}`);
      console.log('API endpoints available at:');
      console.log(`  GET    http://localhost:${PORT}/api/books`);
      console.log(`  POST   http://localhost:${PORT}/api/books`);
      console.log(`  GET    http://localhost:${PORT}/api/books/:id`);
      console.log(`  PUT    http://localhost:${PORT}/api/books/:id`);
      console.log(`  DELETE http://localhost:${PORT}/api/books/:id`);
    });
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
}

startServer();