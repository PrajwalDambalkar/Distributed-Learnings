// routes/auth.js - Authentication routes
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');

// Dummy user data (for demo purposes)
// In production, this would be stored in a database
const users = [
    {
        id: 1,
        username: 'admin',
        password: bcrypt.hashSync('password', 8),
        name: 'Administrator',
        role: 'admin'
    },
    {
        id: 2,
        username: 'student',
        password: bcrypt.hashSync('student123', 8),
        name: 'John Doe',
        role: 'student'
    },
    {
        id: 3,
        username: 'faculty',
        password: bcrypt.hashSync('faculty123', 8),
        name: 'Dr. Jane Smith',
        role: 'faculty'
    }
];

// GET /auth/login - Display login page
router.get('/login', (req, res) => {
    // Redirect to dashboard if already logged in
    if (req.session.user) {
        return res.redirect('/dashboard');
    }
    
    res.render('login', { 
        title: 'Login - ADS-SJSU',
        error: null
    });
});

// POST /auth/login - Handle login form submission
router.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    // Basic validation
    if (!username || !password) {
        return res.render('login', { 
            title: 'Login - ADS-SJSU',
            error: 'Please provide both username and password'
        });
    }
    
    // Find user in our dummy data
    const user = users.find(u => u.username === username);
    
    if (user && bcrypt.compareSync(password, user.password)) {
        // Store user info in session (excluding password)
        req.session.user = {
            id: user.id,
            username: user.username,
            name: user.name,
            role: user.role
        };
        
        console.log('Login successful for:', user.username);
        res.redirect('/dashboard');
    } else {
        console.log('Login failed for username:', username);
        res.render('login', { 
            title: 'Login - ADS-SJSU',
            error: 'Invalid username or password'
        });
    }
});

// GET /auth/logout - Handle logout
router.get('/logout', (req, res) => {
    const username = req.session.user ? req.session.user.username : 'Unknown';
    
    req.session.destroy(err => {
        if (err) {
            console.error('Session destruction error:', err);
            return res.redirect('/dashboard');
        }
        
        console.log('Logout successful for:', username);
        res.redirect('/');
    });
});

module.exports = router;