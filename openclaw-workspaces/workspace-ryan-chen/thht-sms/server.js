const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// OpenPhone API config
const OPENPHONE_API_KEY = process.env.OPENPHONE_API_KEY || 'eBT7xb2iz28sv69Ep8TQhdEQ4iy0yqUP';
const OPENPHONE_PHONE_ID = process.env.OPENPHONE_PHONE_ID || 'PNrlZWRdNH';
const OPENPHONE_FROM_NUMBER = process.env.OPENPHONE_FROM_NUMBER || '+13862733460';

// Data storage
const DATA_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);

const LEADS_FILE = path.join(DATA_DIR, 'leads.json');
const TEMPLATES_FILE = path.join(DATA_DIR, 'templates.json');
const CADENCES_FILE = path.join(DATA_DIR, 'cadences.json');
const SENT_FILE = path.join(DATA_DIR, 'sent.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Initialize data files
function loadData(file, defaultValue = []) {
  if (!fs.existsSync(file)) {
    fs.writeFileSync(file, JSON.stringify(defaultValue, null, 2));
    return defaultValue;
  }
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function saveData(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

// ============ OPENPHONE API ============

async function sendSMS(to, message) {
  const response = await fetch('https://api.openphone.com/v1/messages', {
    method: 'POST',
    headers: {
      'Authorization': OPENPHONE_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: OPENPHONE_FROM_NUMBER,
      to: [to],
      content: message
    })
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message || `API error: ${response.status}`);
  }
  
  return data;
}

// ============ LEADS API ============

app.get('/api/leads', (req, res) => {
  const leads = loadData(LEADS_FILE);
  res.json({ leads, count: leads.length });
});

app.post('/api/leads', (req, res) => {
  const leads = loadData(LEADS_FILE);
  const newLead = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    firstName: req.body.firstName || '',
    lastName: req.body.lastName || '',
    phone: req.body.phone || '',
    address: req.body.address || '',
    city: req.body.city || '',
    source: req.body.source || 'manual',
    status: 'new',
    optedOut: false,
    cadenceId: null,
    cadenceStep: 0,
    lastContacted: null,
    nextContact: null,
    createdAt: new Date().toISOString()
  };
  leads.push(newLead);
  saveData(LEADS_FILE, leads);
  res.status(201).json(newLead);
});

app.post('/api/leads/import', (req, res) => {
  const leads = loadData(LEADS_FILE);
  const imported = req.body.leads || [];
  let count = 0;
  
  for (const l of imported) {
    // Skip if no phone
    if (!l.phone) continue;
    
    // Format phone to E.164
    let phone = l.phone.replace(/\D/g, '');
    if (phone.length === 10) phone = '1' + phone;
    if (!phone.startsWith('+')) phone = '+' + phone;
    
    const newLead = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      firstName: l.firstName || l.first_name || '',
      lastName: l.lastName || l.last_name || '',
      phone: phone,
      address: l.address || l.propertyAddress || '',
      city: l.city || '',
      source: l.source || 'import',
      status: 'new',
      optedOut: false,
      cadenceId: null,
      cadenceStep: 0,
      lastContacted: null,
      nextContact: null,
      createdAt: new Date().toISOString()
    };
    leads.push(newLead);
    count++;
  }
  
  saveData(LEADS_FILE, leads);
  res.json({ imported: count, total: leads.length });
});

app.put('/api/leads/:id/optout', (req, res) => {
  const leads = loadData(LEADS_FILE);
  const idx = leads.findIndex(l => l.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Lead not found' });
  
  leads[idx].optedOut = true;
  leads[idx].status = 'opted-out';
  saveData(LEADS_FILE, leads);
  res.json(leads[idx]);
});

app.delete('/api/leads/:id', (req, res) => {
  let leads = loadData(LEADS_FILE);
  leads = leads.filter(l => l.id !== req.params.id);
  saveData(LEADS_FILE, leads);
  res.json({ success: true });
});

// ============ TEMPLATES API ============

app.get('/api/templates', (req, res) => {
  const templates = loadData(TEMPLATES_FILE);
  res.json({ templates });
});

app.post('/api/templates', (req, res) => {
  const templates = loadData(TEMPLATES_FILE);
  const template = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    name: req.body.name || 'Untitled',
    content: req.body.content || '',
    createdAt: new Date().toISOString()
  };
  templates.push(template);
  saveData(TEMPLATES_FILE, templates);
  res.status(201).json(template);
});

app.put('/api/templates/:id', (req, res) => {
  const templates = loadData(TEMPLATES_FILE);
  const idx = templates.findIndex(t => t.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Template not found' });
  
  templates[idx] = { ...templates[idx], ...req.body, updatedAt: new Date().toISOString() };
  saveData(TEMPLATES_FILE, templates);
  res.json(templates[idx]);
});

app.delete('/api/templates/:id', (req, res) => {
  let templates = loadData(TEMPLATES_FILE);
  templates = templates.filter(t => t.id !== req.params.id);
  saveData(TEMPLATES_FILE, templates);
  res.json({ success: true });
});

// ============ CADENCES API ============

app.get('/api/cadences', (req, res) => {
  const cadences = loadData(CADENCES_FILE);
  res.json({ cadences });
});

app.post('/api/cadences', (req, res) => {
  const cadences = loadData(CADENCES_FILE);
  const cadence = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    name: req.body.name || 'Untitled Cadence',
    steps: req.body.steps || [],
    active: true,
    createdAt: new Date().toISOString()
  };
  // steps format: [{ day: 0, templateId: 'xxx' }, { day: 3, templateId: 'yyy' }]
  cadences.push(cadence);
  saveData(CADENCES_FILE, cadences);
  res.status(201).json(cadence);
});

app.put('/api/cadences/:id', (req, res) => {
  const cadences = loadData(CADENCES_FILE);
  const idx = cadences.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Cadence not found' });
  
  cadences[idx] = { ...cadences[idx], ...req.body, updatedAt: new Date().toISOString() };
  saveData(CADENCES_FILE, cadences);
  res.json(cadences[idx]);
});

// ============ SEND SMS API ============

// Send single SMS
app.post('/api/send', async (req, res) => {
  try {
    const { to, message, leadId } = req.body;
    
    if (!to || !message) {
      return res.status(400).json({ error: 'Missing to or message' });
    }
    
    const result = await sendSMS(to, message);
    
    // Log sent message
    const sent = loadData(SENT_FILE);
    sent.push({
      id: result.data?.id || Date.now().toString(),
      leadId: leadId || null,
      to,
      message,
      status: result.data?.status || 'sent',
      sentAt: new Date().toISOString()
    });
    saveData(SENT_FILE, sent);
    
    // Update lead if provided
    if (leadId) {
      const leads = loadData(LEADS_FILE);
      const idx = leads.findIndex(l => l.id === leadId);
      if (idx !== -1) {
        leads[idx].lastContacted = new Date().toISOString();
        leads[idx].status = 'contacted';
        saveData(LEADS_FILE, leads);
      }
    }
    
    res.json({ success: true, result });
  } catch (error) {
    console.error('Send error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Bulk send with template
app.post('/api/send/bulk', async (req, res) => {
  try {
    const { leadIds, templateId, delayMs = 1000 } = req.body;
    
    const leads = loadData(LEADS_FILE);
    const templates = loadData(TEMPLATES_FILE);
    const template = templates.find(t => t.id === templateId);
    
    if (!template) {
      return res.status(400).json({ error: 'Template not found' });
    }
    
    const results = [];
    const sent = loadData(SENT_FILE);
    
    for (const leadId of leadIds) {
      const lead = leads.find(l => l.id === leadId);
      if (!lead || lead.optedOut || !lead.phone) {
        results.push({ leadId, status: 'skipped', reason: lead?.optedOut ? 'opted-out' : 'no phone' });
        continue;
      }
      
      // Personalize message
      let message = template.content
        .replace(/{firstName}/g, lead.firstName || '')
        .replace(/{lastName}/g, lead.lastName || '')
        .replace(/{address}/g, lead.address || '')
        .replace(/{city}/g, lead.city || '')
        .trim();
      
      try {
        const result = await sendSMS(lead.phone, message);
        results.push({ leadId, status: 'sent', messageId: result.data?.id });
        
        sent.push({
          id: result.data?.id || Date.now().toString(),
          leadId,
          to: lead.phone,
          message,
          status: 'sent',
          sentAt: new Date().toISOString()
        });
        
        // Update lead
        const idx = leads.findIndex(l => l.id === leadId);
        if (idx !== -1) {
          leads[idx].lastContacted = new Date().toISOString();
          leads[idx].status = 'contacted';
        }
        
        // Rate limiting delay
        await new Promise(r => setTimeout(r, delayMs));
        
      } catch (error) {
        results.push({ leadId, status: 'error', error: error.message });
      }
    }
    
    saveData(SENT_FILE, sent);
    saveData(LEADS_FILE, leads);
    
    const successCount = results.filter(r => r.status === 'sent').length;
    res.json({ 
      success: true, 
      sent: successCount, 
      total: leadIds.length,
      results 
    });
    
  } catch (error) {
    console.error('Bulk send error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============ STATS API ============

app.get('/api/stats', (req, res) => {
  const leads = loadData(LEADS_FILE);
  const sent = loadData(SENT_FILE);
  
  const stats = {
    totalLeads: leads.length,
    newLeads: leads.filter(l => l.status === 'new').length,
    contacted: leads.filter(l => l.status === 'contacted').length,
    optedOut: leads.filter(l => l.optedOut).length,
    messagesSent: sent.length,
    messagesToday: sent.filter(s => {
      const today = new Date().toISOString().split('T')[0];
      return s.sentAt?.startsWith(today);
    }).length
  };
  
  res.json(stats);
});

// ============ SENT LOG API ============

app.get('/api/sent', (req, res) => {
  const sent = loadData(SENT_FILE);
  res.json({ sent: sent.slice(-100).reverse() }); // Last 100, newest first
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`THHT SMS Cadence System running on port ${PORT}`);
  console.log(`OpenPhone Number: ${OPENPHONE_FROM_NUMBER}`);
});
