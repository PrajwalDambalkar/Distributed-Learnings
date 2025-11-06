const express = require('express');
require('dotenv').config();
const authRoutes = require('./routes/authRoutes');

const app = express();
app.use(express.json());
app.use('/api/auth', authRoutes);

if (process.env.NODE_ENV !== 'test') {
  app.listen(3000, () => console.log('Server running on port 3000'));
}

module.exports = app;