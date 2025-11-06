// In-memory data store (you can replace this with a real database later)
let items = [
  { id: 1, name: 'Item 1', description: 'First item', quantity: 10 },
  { id: 2, name: 'Item 2', description: 'Second item', quantity: 20 },
  { id: 3, name: 'Item 3', description: 'Third item', quantity: 15 }
];

let nextId = 4;

// GET all items
const getAllItems = (req, res) => {
  res.status(200).json({
    success: true,
    count: items.length,
    data: items
  });
};

// GET single item by ID
const getItemById = (req, res) => {
  const id = parseInt(req.params.id);
  const item = items.find(i => i.id === id);

  if (!item) {
    return res.status(404).json({
      success: false,
      error: 'Item not found'
    });
  }

  res.status(200).json({
    success: true,
    data: item
  });
};

// POST create new item
const createItem = (req, res) => {
  const { name, description, quantity } = req.body;

  // Validation
  if (!name || !description) {
    return res.status(400).json({
      success: false,
      error: 'Name and description are required'
    });
  }

  const newItem = {
    id: nextId++,
    name,
    description,
    quantity: quantity || 0
  };

  items.push(newItem);

  res.status(201).json({
    success: true,
    data: newItem
  });
};

// PUT update item by ID
const updateItem = (req, res) => {
  const id = parseInt(req.params.id);
  const itemIndex = items.findIndex(i => i.id === id);

  if (itemIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Item not found'
    });
  }

  const { name, description, quantity } = req.body;

  // Update only provided fields
  if (name !== undefined) items[itemIndex].name = name;
  if (description !== undefined) items[itemIndex].description = description;
  if (quantity !== undefined) items[itemIndex].quantity = quantity;

  res.status(200).json({
    success: true,
    data: items[itemIndex]
  });
};

// DELETE item by ID
const deleteItem = (req, res) => {
  const id = parseInt(req.params.id);
  const itemIndex = items.findIndex(i => i.id === id);

  if (itemIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Item not found'
    });
  }

  const deletedItem = items.splice(itemIndex, 1)[0];

  res.status(200).json({
    success: true,
    data: deletedItem
  });
};

module.exports = {
  getAllItems,
  getItemById,
  createItem,
  updateItem,
  deleteItem
};
