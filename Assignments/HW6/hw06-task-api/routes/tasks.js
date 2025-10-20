const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// CREATE - POST /api/tasks
router.post('/', async (req, res) => {
  try {
    const task = new Task(req.body);
    await task.save();
    res.status(201).json({
      success: true,
      data: task
    });
  } catch (error) {
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      return res.status(400).json({
        success: false,
        error: messages
      });
    }
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
});

// READ ALL - GET /api/tasks
router.get('/', async (req, res) => {
  try {
    const tasks = await Task.find().sort({ createdAt: -1 });
    res.status(200).json({
      success: true,
      count: tasks.length,
      data: tasks
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
});

// READ ONE - GET /api/tasks/:id
router.get('/:id', async (req, res) => {
  try {
    const task = await Task.findById(req.params.id);
    
    if (!task) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: task
    });
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
});

// UPDATE - PUT /api/tasks/:id
router.put('/:id', async (req, res) => {
  try {
    const task = await Task.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true
      }
    );
    
    if (!task) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: task
    });
  } catch (error) {
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      return res.status(400).json({
        success: false,
        error: messages
      });
    }
    if (error.kind === 'ObjectId') {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
});

// DELETE - DELETE /api/tasks/:id
router.delete('/:id', async (req, res) => {
  try {
    const task = await Task.findByIdAndDelete(req.params.id);
    
    if (!task) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: {},
      message: 'Task deleted successfully'
    });
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }
    res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
});

module.exports = router;