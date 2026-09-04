#!/usr/bin/env node
/**
 * Skip Trace Tool - FREE Contact Info Lookup
 * Searches TruePeopleSearch for phone numbers and emails
 * 
 * Usage: node skip-trace.js input.csv output.csv
 * 
 * Input CSV format (from vcpa-local-match.js output):
 *   Original Name,Confidence,Matched Owner Name,Property Address,City,Parcel ID
 * 
 * Output adds: Phone1, Phone2, Email1, Email2
 */

const fs = require('fs');

// Configuration
const CONFIG = {
  baseUrl: 'https://www.truepeoplesearch.com',
  minDelay: 15000,  // 15 seconds minimum between requests
  maxDelay: 30000,  // 30 seconds maximum
  typeDelay: 50,    // ms between keystrokes
  typeVariance: 100, // random variance in typing speed
  maxRetries: 2,
  userAgents: [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
  ]
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function randomDelay() {
  return CONFIG.minDelay + Math.random() * (CONFIG.maxDelay - CONFIG.minDelay);
}

function randomUserAgent() {
  return CONFIG.userAgents[Math.floor(Math.random() * CONFIG.userAgents.length)];
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

async function humanType(page, selector, text) {
  await page.click(selector);
  for (const char of text) {
    await page.keyboard.type(char);
    await sleep(CONFIG.typeDelay + Math.random() * CONFIG.typeVariance);
  }
}

async function humanScroll(page) {
  // Random scroll behavior
  const scrolls = Math.floor(Math.random() * 3) + 1;
  for (let i = 0; i < scrolls; i++) {
    await page.evaluate(() => {
      window.scrollBy(0, 200 + Math.random() * 300);
    });
    await sleep(500 + Math.random() * 1000);
  }
}

async function searchPerson(page, name, city, state = 'FL') {
  const result = {
    phones: [],
    emails: [],
    address: '',
    age: ''
  };
  
  try {
    // Build search URL
    const nameParts = name.split(/\s+/);
    const firstName = nameParts[0] || '';
    const lastName = nameParts[nameParts.length - 1] || '';
    
    const searchUrl = `${CONFIG.baseUrl}/results?name=${encodeURIComponent(firstName + ' ' + lastName)}&citystatezip=${encodeURIComponent(city + ', ' + state)}`;
    
    // Navigate with random delay
    await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(2000 + Math.random() * 2000);
    
    // Human-like scrolling
    await humanScroll(page);
    
    // Look for result cards
    const cards = await page.$$('.card-summary');
    
    if (cards.length === 0) {
      return { ...result, status: 'NO_RESULTS' };
    }
    
    // Click first matching result
    const firstCard = cards[0];
    await firstCard.click();
    await sleep(2000 + Math.random() * 2000);
    
    // Extract phone numbers
    const phoneElements = await page.$$('[data-link-to-more="phone"] a, .phone');
    for (const el of phoneElements.slice(0, 3)) {
      const phone = await el.textContent();
      if (phone && phone.match(/\d{3}.*\d{3}.*\d{4}/)) {
        result.phones.push(phone.trim());
      }
    }
    
    // Extract emails
    const emailElements = await page.$$('[data-link-to-more="email"] a, .email');
    for (const el of emailElements.slice(0, 3)) {
      const email = await el.textContent();
      if (email && email.includes('@')) {
        result.emails.push(email.trim());
      }
    }
    
    // Try alternate selectors if needed
    if (result.phones.length === 0) {
      const allLinks = await page.$$('a[href^="tel:"]');
      for (const el of allLinks.slice(0, 3)) {
        const phone = await el.textContent();
        if (phone) result.phones.push(phone.trim());
      }
    }
    
    if (result.emails.length === 0) {
      const allLinks = await page.$$('a[href^="mailto:"]');
      for (const el of allLinks.slice(0, 3)) {
        const email = await el.textContent();
        if (email) result.emails.push(email.trim());
      }
    }
    
    result.status = (result.phones.length > 0 || result.emails.length > 0) ? 'FOUND' : 'NO_CONTACT';
    
  } catch (error) {
    result.status = 'ERROR';
    result.error = error.message;
  }
  
  return result;
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node skip-trace.js <input.csv> <output.csv>');
    console.log('');
    console.log('Input: CSV from vcpa-local-match.js (needs Name and City columns)');
    process.exit(1);
  }
  
  const inputFile = args[0];
  const outputFile = args[1];
  
  // Check input
  if (!fs.existsSync(inputFile)) {
    console.error(`Error: Input file not found: ${inputFile}`);
    process.exit(1);
  }
  
  console.log('\n🔍 Skip Trace Tool - FREE Contact Lookup');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Input: ${inputFile}`);
  console.log(`Output: ${outputFile}`);
  console.log(`Delay: ${CONFIG.minDelay/1000}-${CONFIG.maxDelay/1000} seconds between searches`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  
  // Parse input
  const content = fs.readFileSync(inputFile, 'utf8');
  const lines = content.trim().split('\n');
  const headers = parseCSVLine(lines[0]);
  
  // Find column indices
  const nameCol = headers.findIndex(h => h.toLowerCase().includes('matched owner') || h.toLowerCase().includes('owner name'));
  const cityCol = headers.findIndex(h => h.toLowerCase() === 'city');
  const origNameCol = headers.findIndex(h => h.toLowerCase().includes('original'));
  
  if (nameCol === -1) {
    console.error('Error: Could not find owner name column');
    process.exit(1);
  }
  
  // Load records
  const records = [];
  const seen = new Set(); // Deduplicate by name+city
  
  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    const name = values[nameCol]?.replace(/"/g, '').trim();
    const city = values[cityCol]?.replace(/"/g, '').trim() || 'FL';
    const origName = values[origNameCol]?.replace(/"/g, '').trim() || name;
    
    if (!name || name === 'NO MATCH FOUND' || name.includes('ERROR')) continue;
    
    const key = `${name}|${city}`;
    if (seen.has(key)) continue;
    seen.add(key);
    
    records.push({ name, city, origName, values });
  }
  
  console.log(`📋 Loaded ${records.length} unique leads to search\n`);
  
  // Initialize browser
  let browser, page;
  try {
    const { chromium } = require('playwright');
    browser = await chromium.launch({ 
      headless: true,
      args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext({
      userAgent: randomUserAgent(),
      viewport: { width: 1366, height: 768 },
      locale: 'en-US',
      timezoneId: 'America/New_York'
    });
    
    page = await context.newPage();
    
    // Add stealth
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });
    
  } catch (err) {
    console.error('Error: Playwright not available. Run: npm install playwright');
    process.exit(1);
  }
  
  // Process records
  const results = [];
  let foundCount = 0;
  let noContactCount = 0;
  let errorCount = 0;
  
  for (let i = 0; i < records.length; i++) {
    const { name, city, origName, values } = records[i];
    
    console.log(`[${i + 1}/${records.length}] Searching: ${name}, ${city}...`);
    
    const result = await searchPerson(page, name, city);
    
    if (result.status === 'FOUND') {
      console.log(`  ✅ Found: ${result.phones.length} phone(s), ${result.emails.length} email(s)`);
      foundCount++;
    } else if (result.status === 'NO_CONTACT') {
      console.log(`  ⚠️ Found person but no contact info`);
      noContactCount++;
    } else if (result.status === 'NO_RESULTS') {
      console.log(`  ❌ No results found`);
      noContactCount++;
    } else {
      console.log(`  ❌ Error: ${result.error || 'Unknown'}`);
      errorCount++;
    }
    
    results.push({
      origName,
      name,
      city,
      phone1: result.phones[0] || '',
      phone2: result.phones[1] || '',
      email1: result.emails[0] || '',
      email2: result.emails[1] || '',
      status: result.status
    });
    
    // Save progress every 10 records
    if ((i + 1) % 10 === 0) {
      saveResults(outputFile, results);
      console.log(`  💾 Progress saved (${i + 1}/${records.length})\n`);
    }
    
    // Random delay before next search
    if (i < records.length - 1) {
      const delay = randomDelay();
      console.log(`  ⏳ Waiting ${Math.round(delay/1000)}s...\n`);
      await sleep(delay);
    }
  }
  
  // Close browser
  await browser.close();
  
  // Save final results
  saveResults(outputFile, results);
  
  // Summary
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('✅ Complete!');
  console.log(`   Total searched: ${records.length}`);
  console.log(`   📞 With contact info: ${foundCount}`);
  console.log(`   ⚠️ No contact found: ${noContactCount}`);
  console.log(`   ❌ Errors: ${errorCount}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`   Output: ${outputFile}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

function saveResults(outputFile, results) {
  const headers = ['Original Name', 'Matched Owner', 'City', 'Phone 1', 'Phone 2', 'Email 1', 'Email 2', 'Status'];
  const lines = [headers.join(',')];
  
  for (const r of results) {
    lines.push([
      `"${r.origName}"`,
      `"${r.name}"`,
      `"${r.city}"`,
      `"${r.phone1}"`,
      `"${r.phone2}"`,
      `"${r.email1}"`,
      `"${r.email2}"`,
      `"${r.status}"`
    ].join(','));
  }
  
  fs.writeFileSync(outputFile, lines.join('\n'));
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
