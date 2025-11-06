const express = require('express');
const jwt = require('jsonwebtoken');
const verifyToken = require('../middleware/verifyToken');

const router = express.Router();

// Helper to get test tokens
router.get('/tokens', (req, res) => {
  const userToken = jwt.sign({ role: 'user' }, process.env.JWT_SECRET);
  const adminToken = jwt.sign({ role: 'admin' }, process.env.JWT_SECRET);
  res.json({ userToken, adminToken });
});

// QUESTION 1: Protected route (admin OR user)
router.get('/protected/user-status', verifyToken, (req, res) => {
  // 1. Check for 'admin' OR 'user' role
  if (req.user.role !== 'admin' && req.user.role !== 'user') {
    // 2. If Authorization fails, send 403 Forbidden
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  // 3. If Authorization succeeds, send 200 OK
  res.status(200).json({ 
    message: 'Access granted',
    user: req.user 
  });
});

// BONUS: Admin-only route (like your friend's implementation)
router.get('/protected/admin-data', verifyToken, (req, res) => {
  // Check for 'admin' role ONLY
  if (req.user.role !== 'admin') {
    // If not admin, send 403 Forbidden
    return res.status(403).json({ error: 'Forbidden: Admin access required' });
  }
  
  // If admin, send 200 OK with admin data
  res.status(200).json({ 
    message: 'Admin access granted',
    data: 'Sensitive admin data here',
    user: req.user 
  });
});

module.exports = router;