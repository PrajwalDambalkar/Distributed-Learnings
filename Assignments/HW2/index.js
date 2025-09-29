//import express module 
const express = require('express');
//create an express app
const  app = express();
//require express middleware body-parser
const bodyParser = require('body-parser');

//set the view engine to ejs
app.set('view engine', 'ejs');
//set the directory of views
app.set('views', './views');
//specify the path of static directory
app.use(express.static(__dirname + '/public'));

//use body parser to parse JSON and urlencoded request bodies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

//By Default we have 3 books
var books = [
    { "BookID": "1", "Title": "The Brothers Karamazov", "Author": "Fyodor Dostoevsky" },
    { "BookID": "2", "Title": "Invisible Man", "Author": "Ralph Ellison" },
    { "BookID": "3", "Title": "Middlemarch", "Author": "George Eliot" },
    { "BookID": "4", "Title": "Slaughterhouse-Five", "Author": "Kurt Vonnegut" },
    { "BookID": "5", "Title": "Things Fall Apart", "Author": "Chinua Achebe" }
]

//route to root
app.get('/', function (req, res) {
    res.render('home', {
        books: books
    });
});

// ========== CREATE OPERATIONS ==========
// Route to render the create view
app.get('/add-book', function (req, res) {
    res.render('create');
});

// Route to create new book (Question 1)
app.post('/add-book', function (req, res) {
    // Get the highest ID and increment it
    const highestId = books.length > 0 ? Math.max(...books.map(book => parseInt(book.BookID))) : 0;
    const newId = (highestId + 1).toString();
    
    // Create new book object
    const newBook = {
        "BookID": newId,
        "Title": req.body.title,
        "Author": req.body.author
    };
    
    // Add to books array
    books.push(newBook);
    
    // Redirect to home view
    res.redirect('/');
});

// ========== UPDATE OPERATIONS ==========
// Route to render the update view
app.get('/update-book', function (req, res) {
    res.render('update');
});

// Route to update book (Question 2) - Fixed for proper ID matching
app.post('/update-book', function (req, res) {
    // Get the book ID and new values from the form
    const bookId = req.body.id.toString(); // Convert to string to match existing IDs
    const newTitle = req.body.title;
    const newAuthor = req.body.author;
    
    console.log('Updating book with ID:', bookId); // Debug log
    console.log('New title:', newTitle); // Debug log
    console.log('New author:', newAuthor); // Debug log
    
    // Find book with the specified ID
    const bookIndex = books.findIndex(book => book.BookID === bookId);
    
    console.log('Found book at index:', bookIndex); // Debug log
    
    if (bookIndex !== -1) {
        // Update the book with the new values
        books[bookIndex] = {
            "BookID": bookId,
            "Title": newTitle,
            "Author": newAuthor
        };
        console.log('Book updated successfully'); // Debug log
    } else {
        console.log('Book not found with ID:', bookId); // Debug log
    }
    
    // Redirect to home view
    res.redirect('/');
});

// ========== DELETE OPERATIONS ==========
// Route to render the delete view
app.get('/delete-book', function (req, res) {
    res.render('delete');
});

// Route to delete book with highest ID (Question 3)
app.post('/delete-book', function (req, res) {
    if (books.length > 0) {
        // Find the highest ID
        const highestId = Math.max(...books.map(book => parseInt(book.BookID)));
        
        // Filter out the book with highest ID
        books = books.filter(book => parseInt(book.BookID) !== highestId);
    }
    
    // Redirect to home view
    res.redirect('/');
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, function () {
    console.log(`Server listening on port ${PORT}`);
});

// var books = [
//     { "BookID": "1", "Title": "The Brothers Karamazov", "Author": "Fyodor Dostoevsky" },
//     { "BookID": "2", "Title": "Invisible Man", "Author": "Ralph Ellison" },
//     { "BookID": "3", "Title": "Middlemarch", "Author": "George Eliot" },
//     { "BookID": "4", "Title": "Slaughterhouse-Five", "Author": "Kurt Vonnegut" },
//     { "BookID": "5", "Title": "Things Fall Apart", "Author": "Chinua Achebe" }
// ]