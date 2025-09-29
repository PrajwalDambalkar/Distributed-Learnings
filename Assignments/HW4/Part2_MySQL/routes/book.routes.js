const express = require('express');
const router = express.Router();
const bookController = require('../controllers/book.controller');

// POST /books - Create a new book
router.post('/books', bookController.createBook);

// GET /books - Get all books
router.get('/books', bookController.getAllBooks);

// GET /books/:id - Get book by ID
router.get('/books/:id', bookController.getBookById);

// PUT /books/:id - Update a book
router.put('/books/:id', bookController.updateBook);

// DELETE /books/:id - Delete a book
router.delete('/books/:id', bookController.deleteBook);

module.exports = router;