// app.js - Main application file
// Load environment variables first
require('dotenv').config();

const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const path = require('path');

// Import routes
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Session configuration
app.use(session({
    secret: process.env.SESSION_SECRET || 'ads-sjsu-super-secret-key-2024',
    resave: false,
    saveUninitialized: true,
    cookie: { 
        secure: false, // Set to true if using HTTPS in production
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));

// Set EJS as the templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Serve static files (CSS, JS, images)
app.use(express.static(path.join(__dirname, 'public')));

// Session debugging middleware - logs session data for each request
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    console.log('Session Data:', req.session.user ? 
        `User: ${req.session.user.username} (${req.session.user.name})` : 
        'No user session'
    );
    next();
});

// Routes
// Home route
app.get('/', (req, res) => {
    res.render('index', { 
        user: req.session.user,
        title: 'ADS-SJSU Authentication System'
    });
});

// Protected dashboard route
app.get('/dashboard', (req, res) => {
    if (!req.session.user) {
        console.log('Unauthorized access attempt to dashboard');
        return res.redirect('/auth/login');
    }
    
    console.log('Dashboard access granted for:', req.session.user.username);
    res.render('dashboard', { 
        user: req.session.user,
        title: 'Dashboard - ADS-SJSU'
    });
});

// Use authentication routes with /auth prefix
app.use('/auth', authRoutes);

// 404 handler
app.use('*', (req, res) => {
    console.log('404 - Page not found:', req.originalUrl);
    res.status(404).render('index', { 
        user: req.session.user,
        title: 'Page Not Found - ADS-SJSU',
        error: `Page "${req.originalUrl}" not found. Please check the URL or return to home.`
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Server Error:', err.stack);
    res.status(500).send(`
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #dc3545;">Something went wrong!</h2>
            <p>The server encountered an internal error. Please try again later.</p>
            <p><a href="/" style="color: #007bff; text-decoration: none;">← Return to Home</a></p>
            <hr>
            <small style="color: #666;">Error ID: ${Date.now()}</small>
        </div>
    `);
});

// Start the server
app.listen(PORT, () => {
    console.log(' ==========================================');
    console.log(` ADS-SJSU Auth Server is running!`);
    console.log(` URL: http://localhost:${PORT}`);
    console.log(` Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(' Available Routes:');
    console.log('   GET  /              - Home page');
    console.log('   GET  /auth/login    - Login page');
    console.log('   POST /auth/login    - Login form handler');
    console.log('   GET  /auth/logout   - Logout handler');
    console.log('   GET  /dashboard     - Protected dashboard');
    console.log(' ==========================================');
});