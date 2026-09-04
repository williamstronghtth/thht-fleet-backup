#!/usr/bin/env node
/**
 * VCPA Property Lookup Tool
 * Cross-references names against Volusia County Property Appraiser database
 * 
 * Usage: node vcpa-lookup.js input.csv output.csv
 * 
 * Input CSV format:
 *   Last Name,First Name
 *   Smith,John
 *   Johnson,Mary
 * 
 * Output CSV format:
 *   Original Name,Matched Owner Name,Property Address,City,Parcel ID,Property Class
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  baseUrl: 'https://vcpa.vcgov.org/search/real-property-classic',
  delayBetweenRequests: 2000, // 2 seconds between searches
  maxResultsPerName: 100, // Cap results to avoid huge datasets
  timeout: 30000 // 30 second timeout per request
};

// Property class code mapping
const PROPERTY_CLASSES = {
  '0000': 'Vacant Residential',
  '0100': 'Single Family',
  '0200': 'Mobile Home',
  '0300': 'Multi-Family >10',
  '0400': 'Condominium',
  '0500': 'Cooperatives',
  '0600': 'Retirement',
  '0700': 'Misc Residence',
  '0800': 'Multi-Family <10',
  '5300': 'Cropland Class 3',
  '5600': 'Timberland',
  '6900': 'Ornamental/Misc Agri',
  '9900': 'Non-Agricultural'
};

function parseCSV(content) {
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  const records = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    if (values.length >= 2 && values[0] && values[1]) {
      records.push({
        lastName: values[0].replace(/"/g, ''),
        firstName: values[1].replace(/"/g, '')
      });
    }
  }
  return records;
}

function formatSearchName(lastName, firstName) {
  // Search by LAST NAME ONLY for broader matching
  // We'll filter and score results by first name match
  return lastName.toUpperCase();
}

function calculateConfidence(searchFirstName, matchedOwnerName) {
  const firstName = searchFirstName.toUpperCase();
  const ownerUpper = matchedOwnerName.toUpperCase();
  
  // Extract first name from owner (format: "LASTNAME FIRSTNAME M" or "LASTNAME FIRSTNAME & SPOUSE")
  const parts = ownerUpper.split(/\s+/);
  if (parts.length < 2) return { tier: 'LOW', score: 1 };
  
  // Get potential first name (second word after last name)
  const ownerFirstName = parts[1];
  
  // HIGH: Exact first name match
  if (ownerFirstName === firstName) {
    return { tier: 'HIGH', score: 3 };
  }
  
  // HIGH: First name starts with search (e.g., "JOHN" matches "JOHNNY")
  if (ownerFirstName.startsWith(firstName) && firstName.length >= 3) {
    return { tier: 'HIGH', score: 3 };
  }
  
  // MEDIUM: Search starts with owner first name (e.g., "JOHNNY" matches "JOHN")
  if (firstName.startsWith(ownerFirstName) && ownerFirstName.length >= 3) {
    return { tier: 'MEDIUM', score: 2 };
  }
  
  // MEDIUM: First 3+ chars match (handles typos, abbreviations)
  if (firstName.length >= 3 && ownerFirstName.length >= 3 && 
      firstName.substring(0, 3) === ownerFirstName.substring(0, 3)) {
    return { tier: 'MEDIUM', score: 2 };
  }
  
  // LOW: Last name only match
  return { tier: 'LOW', score: 1 };
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function searchVCPA(page, searchName) {
  const results = [];
  
  try {
    // Navigate to search page
    await page.goto(CONFIG.baseUrl, { waitUntil: 'domcontentloaded', timeout: CONFIG.timeout });
    
    // Wait for the page to fully load
    await sleep(2000);
    
    // Clear and fill owner name field - use ID selector
    const ownerField = await page.waitForSelector('#ownername', { state: 'attached', timeout: 15000 });
    if (ownerField) {
      // Scroll into view and make visible if needed
      await ownerField.scrollIntoViewIfNeeded();
      await ownerField.click({ force: true });
      await ownerField.fill('');
      await ownerField.fill(searchName);
    } else {
      throw new Error('Owner Name field not found');
    }
    
    // Click search button
    await page.click('button:has-text("Search")');
    
    // Wait for results
    await page.waitForSelector('table tbody tr', { timeout: 10000 }).catch(() => null);
    await sleep(1000); // Extra wait for dynamic content
    
    // Check for "No matches found"
    const noMatches = await page.$('text="No matches found"');
    if (noMatches) {
      return [{ noMatch: true }];
    }
    
    // Get result count
    const statusText = await page.textContent('div[class*="status"], .dataTables_info');
    const countMatch = statusText?.match(/of ([\d,]+) entries/);
    const totalResults = countMatch ? parseInt(countMatch[1].replace(',', '')) : 0;
    
    // Change to show 100 entries if many results
    if (totalResults > 10) {
      const showDropdown = await page.$('select[name*="length"], .dataTables_length select');
      if (showDropdown) {
        await showDropdown.selectOption('100');
        await sleep(1500);
      }
    }
    
    // Extract results from table
    const rows = await page.$$('table tbody tr');
    for (const row of rows) {
      const cells = await row.$$('td');
      if (cells.length >= 6) {
        const altKey = await cells[0].textContent();
        const parcelId = await cells[1].textContent();
        const ownerName = await cells[2].textContent();
        const address = await cells[3].textContent();
        const city = await cells[4].textContent();
        const pc = await cells[5].textContent();
        
        // Skip header rows or empty rows
        if (altKey && !altKey.includes('AltKey')) {
          results.push({
            altKey: altKey.trim(),
            parcelId: parcelId.trim(),
            ownerName: ownerName.trim(),
            address: address.trim(),
            city: city.trim(),
            propertyClass: pc.trim(),
            propertyClassDesc: PROPERTY_CLASSES[pc.trim()] || pc.trim()
          });
        }
      }
      
      // Cap results
      if (results.length >= CONFIG.maxResultsPerName) break;
    }
    
  } catch (error) {
    console.error(`  Error searching "${searchName}": ${error.message}`);
    return [{ error: error.message }];
  }
  
  return results;
}

function generateOutputCSV(results) {
  const headers = ['Original Name', 'Confidence', 'Matched Owner Name', 'Property Address', 'City', 'Parcel ID', 'Property Class'];
  const lines = [headers.join(',')];
  
  // Sort by confidence (HIGH first, then MEDIUM, then LOW)
  const sorted = [...results].sort((a, b) => (b.confidenceScore || 0) - (a.confidenceScore || 0));
  
  for (const result of sorted) {
    const row = [
      `"${result.originalName}"`,
      `"${result.confidence || ''}"`,
      `"${result.matchedOwner || 'NO MATCH FOUND'}"`,
      `"${result.address || ''}"`,
      `"${result.city || ''}"`,
      `"${result.parcelId || ''}"`,
      `"${result.propertyClass || ''}"`
    ];
    lines.push(row.join(','));
  }
  
  return lines.join('\n');
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node vcpa-lookup.js <input.csv> <output.csv>');
    console.log('');
    console.log('Input CSV format:');
    console.log('  Last Name,First Name');
    console.log('  Smith,John');
    console.log('  Johnson,Mary');
    process.exit(1);
  }
  
  const inputFile = args[0];
  const outputFile = args[1];
  
  // Check input file exists
  if (!fs.existsSync(inputFile)) {
    console.error(`Error: Input file not found: ${inputFile}`);
    process.exit(1);
  }
  
  // Parse input
  const csvContent = fs.readFileSync(inputFile, 'utf8');
  const names = parseCSV(csvContent);
  
  console.log(`\n📋 VCPA Property Lookup Tool`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Input: ${inputFile} (${names.length} names)`);
  console.log(`Output: ${outputFile}`);
  console.log(`Delay: ${CONFIG.delayBetweenRequests}ms between requests`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  
  // Initialize browser (using Playwright)
  let browser, page;
  try {
    const { chromium } = require('playwright');
    browser = await chromium.launch({ 
      headless: true,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-setuid-sandbox'
      ]
    });
    page = await browser.newPage({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    // Add stealth settings
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
    });
  } catch (err) {
    console.error('Error: Playwright not available. Install with: npm install playwright');
    console.error('This script requires browser automation to work with VCPA.');
    process.exit(1);
  }
  
  const allResults = [];
  let matchCount = 0;
  let noMatchCount = 0;
  let errorCount = 0;
  
  for (let i = 0; i < names.length; i++) {
    const { lastName, firstName } = names[i];
    const searchName = formatSearchName(lastName, firstName);
    const originalName = `${lastName}, ${firstName}`;
    
    console.log(`[${i + 1}/${names.length}] Searching: ${searchName}...`);
    
    const results = await searchVCPA(page, searchName);
    
    if (results.length === 0 || results[0].noMatch) {
      console.log(`  ❌ No matches found`);
      noMatchCount++;
      allResults.push({
        originalName,
        matchedOwner: null,
        address: null,
        city: null,
        parcelId: null,
        propertyClass: null
      });
    } else if (results[0].error) {
      console.log(`  ⚠️ Error: ${results[0].error}`);
      errorCount++;
      allResults.push({
        originalName,
        confidence: 'ERROR',
        confidenceScore: 0,
        matchedOwner: `ERROR: ${results[0].error}`,
        address: null,
        city: null,
        parcelId: null,
        propertyClass: null
      });
    } else {
      // Calculate confidence for each result
      const scoredResults = results.map(r => {
        const conf = calculateConfidence(firstName, r.ownerName);
        return { ...r, confidence: conf.tier, confidenceScore: conf.score };
      });
      
      // Count by tier
      const highCount = scoredResults.filter(r => r.confidence === 'HIGH').length;
      const medCount = scoredResults.filter(r => r.confidence === 'MEDIUM').length;
      const lowCount = scoredResults.filter(r => r.confidence === 'LOW').length;
      
      console.log(`  ✅ Found ${results.length} properties (HIGH: ${highCount}, MED: ${medCount}, LOW: ${lowCount})`);
      matchCount++;
      
      for (const r of scoredResults) {
        allResults.push({
          originalName,
          confidence: r.confidence,
          confidenceScore: r.confidenceScore,
          matchedOwner: r.ownerName,
          address: r.address,
          city: r.city,
          parcelId: r.parcelId,
          propertyClass: r.propertyClassDesc
        });
      }
    }
    
    // Delay between requests (except for last one)
    if (i < names.length - 1) {
      await sleep(CONFIG.delayBetweenRequests);
    }
    
    // Save progress every 10 names
    if ((i + 1) % 10 === 0) {
      const progressFile = outputFile.replace('.csv', '_progress.csv');
      fs.writeFileSync(progressFile, generateOutputCSV(allResults));
      console.log(`  📁 Progress saved to ${progressFile}`);
    }
  }
  
  // Close browser
  await browser.close();
  
  // Write final output
  const outputContent = generateOutputCSV(allResults);
  fs.writeFileSync(outputFile, outputContent);
  
  // Calculate confidence breakdown
  const highTotal = allResults.filter(r => r.confidence === 'HIGH').length;
  const medTotal = allResults.filter(r => r.confidence === 'MEDIUM').length;
  const lowTotal = allResults.filter(r => r.confidence === 'LOW').length;
  
  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`✅ Complete!`);
  console.log(`   Names searched: ${names.length}`);
  console.log(`   With matches: ${matchCount}`);
  console.log(`   No matches: ${noMatchCount}`);
  console.log(`   Errors: ${errorCount}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📊 Confidence Breakdown:`);
  console.log(`   🟢 HIGH:   ${highTotal} records`);
  console.log(`   🟡 MEDIUM: ${medTotal} records`);
  console.log(`   🔴 LOW:    ${lowTotal} records`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`   Total records: ${allResults.length}`);
  console.log(`   Output: ${outputFile}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
