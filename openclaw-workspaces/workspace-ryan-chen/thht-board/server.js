const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Initialize data file if it doesn't exist
function loadData() {
  if (!fs.existsSync(DATA_FILE)) {
    const initial = {
      columns: ['backlog', 'todo', 'in-progress', 'review', 'done'],
      cards: []
    };
    fs.writeFileSync(DATA_FILE, JSON.stringify(initial, null, 2));
    return initial;
  }
  return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
}

function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// GET all cards
app.get('/api/cards', (req, res) => {
  const data = loadData();
  res.json(data);
});

// POST new card
app.post('/api/cards', (req, res) => {
  const data = loadData();
  const card = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    title: req.body.title || 'Untitled',
    description: req.body.description || '',
    column: req.body.column || 'backlog',
    assignee: req.body.assignee || 'both',
    priority: req.body.priority || 'normal',
    category: req.body.category || 'admin',
    dueDate: req.body.dueDate || null,
    recurring: req.body.recurring || false,
    recurringSchedule: req.body.recurringSchedule || null,
    notes: req.body.notes || '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  data.cards.push(card);
  saveData(data);
  res.status(201).json(card);
});

// PUT update card
app.put('/api/cards/:id', (req, res) => {
  const data = loadData();
  const idx = data.cards.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Card not found' });

  data.cards[idx] = {
    ...data.cards[idx],
    ...req.body,
    id: data.cards[idx].id,
    createdAt: data.cards[idx].createdAt,
    updatedAt: new Date().toISOString()
  };
  saveData(data);
  res.json(data.cards[idx]);
});

// DELETE card
app.delete('/api/cards/:id', (req, res) => {
  const data = loadData();
  data.cards = data.cards.filter(c => c.id !== req.params.id);
  saveData(data);
  res.json({ success: true });
});

// Move card to a different column
app.patch('/api/cards/:id/move', (req, res) => {
  const data = loadData();
  const idx = data.cards.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Card not found' });

  data.cards[idx].column = req.body.column;
  data.cards[idx].updatedAt = new Date().toISOString();
  saveData(data);
  res.json(data.cards[idx]);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Kanban board running on port ${PORT}`);
});
