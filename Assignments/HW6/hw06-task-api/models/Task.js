const mongoose = require('mongoose');

const taskSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Title is required'],
    maxlength: [100, 'Title cannot exceed 100 characters'],
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  status: {
    type: String,
    enum: {
      values: ['pending', 'in-progress', 'completed'],
      message: '{VALUE} is not a valid status'
    },
    default: 'pending'
  },
  priority: {
    type: String,
    enum: {
      values: ['low', 'medium', 'high'],
      message: '{VALUE} is not a valid priority'
    },
    default: 'medium'
  },
  dueDate: {
    type: Date,
    required: [true, 'Due date is required']
  },
  category: {
    type: String,
    enum: {
      values: ['Work', 'Personal', 'Shopping', 'Health', 'Other'],
      message: '{VALUE} is not a valid category'
    },
    required: [true, 'Category is required']
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Task', taskSchema);