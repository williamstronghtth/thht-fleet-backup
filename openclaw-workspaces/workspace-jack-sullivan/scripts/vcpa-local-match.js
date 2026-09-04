#!/usr/bin/env node
/**
 * VCPA Local Property Matcher (FAST VERSION)
 * Matches names against downloaded VCPA database - NO WEB SCRAPING
 * 
 * Usage: node vcpa-local-match.js input.csv output.csv
 * 
 * Prerequisites:
 *   - VCPA database CSVs in /tmp/ (vcpa_owners.csv, vcpa_situs.csv)
 *   - Run vcpa-download-db.sh first if not present
 */

const fs = require('fs');
const readline = require('readline');

// Configuration
const CONFIG = {
  ownersFile: '/tmp/vcpa_owners.csv',
  situsFile: '/tmp/vcpa_situs.csv',
};

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

async function loadCSV(filePath, processor) {
  const results = [];
  const fileStream = fs.createReadStream(filePath);
  const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });
  
  let isFirst = true;
  let headers = [];
  
  for await (const line of rl) {
    if (isFirst) {
      headers = parseCSVLine(line);
      isFirst = false;
      continue;
    }
    
    const values = parseCSVLine(line);
    const record = {};
    headers.forEach((h, i) => record[h] = values[i] || '');
    
    const processed = processor(record);
    if (processed) results.push(processed);
  }
  
  return results;
}

function calculateConfidence(searchFirstName, ownerName) {
  const firstName = searchFirstName.toUpperCase().trim();
  const ownerUpper = ownerName.toUpperCase();
  
  // Extract first name from owner (format: "LASTNAME FIRSTNAME M")
  const parts = ownerUpper.split(/\s+/);
  if (parts.length < 2) return { tier: 'LOW', score: 1 };
  
  const ownerFirstName = parts[1];
  
  // HIGH: Exact first name match
  if (ownerFirstName === firstName) {
    return { tier: 'HIGH', score: 3 };
  }
  
  // HIGH: First name starts with search
  if (ownerFirstName.startsWith(firstName) && firstName.length >= 3) {
    return { tier: 'HIGH', score: 3 };
  }
  
  // MEDIUM: Search starts with owner first name
  if (firstName.startsWith(ownerFirstName) && ownerFirstName.length >= 3) {
    return { tier: 'MEDIUM', score: 2 };
  }
  
  // MEDIUM: First 3+ chars match
  if (firstName.length >= 3 && ownerFirstName.length >= 3 && 
      firstName.substring(0, 3) === ownerFirstName.substring(0, 3)) {
    return { tier: 'MEDIUM', score: 2 };
  }
  
  return { tier: 'LOW', score: 1 };
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node vcpa-local-match.js <input.csv> <output.csv>');
    console.log('');
    console.log('Input CSV format:');
    console.log('  Last Name,First Name');
    console.log('  Smith,John');
    process.exit(1);
  }
  
  const inputFile = args[0];
  const outputFile = args[1];
  
  // Check prerequisites
  if (!fs.existsSync(CONFIG.ownersFile)) {
    console.error(`Error: VCPA database not found at ${CONFIG.ownersFile}`);
    console.error('Run the database download first.');
    process.exit(1);
  }
  
  console.log('\n📋 VCPA Local Property Matcher');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('Loading VCPA database (this may take a minute)...\n');
  
  // Load owners - index by last name for fast lookup
  console.log('  Loading owners...');
  const ownersByLastName = {};
  await loadCSV(CONFIG.ownersFile, (r) => {
    if (!r.OWN1) return null;
    const ownerName = r.OWN1.replace(/"/g, '').toUpperCase();
    const lastName = ownerName.split(/\s+/)[0];
    
    if (!ownersByLastName[lastName]) ownersByLastName[lastName] = [];
    ownersByLastName[lastName].push({
      parcelId: r.PARID,
      ownerName: ownerName,
      ownerSeq: r.OWNSEQ
    });
    return null; // Don't collect, we indexed directly
  });
  const lastNameCount = Object.keys(ownersByLastName).length;
  console.log(`  ✓ Indexed ${lastNameCount} unique last names`);
  
  // Load situs (addresses) - index by parcel ID
  console.log('  Loading addresses...');
  const addressByParcel = {};
  await loadCSV(CONFIG.situsFile, (r) => {
    if (!r.PARID) return null;
    
    // Build full address
    const parts = [r.ADRNO, r.ADRDIR, r.ADRSTR, r.ADRSUF].filter(p => p);
    const address = parts.join(' ');
    
    addressByParcel[r.PARID] = {
      address: address,
      city: r.CITYNAME || '',
      zip: r.ZIP1 || ''
    };
    return null;
  });
  console.log(`  ✓ Indexed ${Object.keys(addressByParcel).length} addresses`);
  
  // Load input names
  console.log(`  Loading input file: ${inputFile}`);
  const inputContent = fs.readFileSync(inputFile, 'utf8');
  const inputLines = inputContent.trim().split('\n');
  const names = [];
  
  for (let i = 1; i < inputLines.length; i++) {
    const parts = parseCSVLine(inputLines[i]);
    if (parts.length >= 2 && parts[0] && parts[1]) {
      names.push({
        lastName: parts[0].replace(/"/g, '').toUpperCase().trim(),
        firstName: parts[1].replace(/"/g, '').toUpperCase().trim()
      });
    }
  }
  console.log(`  ✓ Loaded ${names.length} names to search\n`);
  
  // Match!
  console.log('🔍 Matching names...\n');
  const results = [];
  let matchCount = 0;
  let noMatchCount = 0;
  
  for (let i = 0; i < names.length; i++) {
    const { lastName, firstName } = names[i];
    const originalName = `${lastName}, ${firstName}`;
    
    // Find all owners with this last name
    const candidates = ownersByLastName[lastName] || [];
    
    if (candidates.length === 0) {
      noMatchCount++;
      results.push({
        originalName,
        confidence: '',
        confidenceScore: 0,
        matchedOwner: 'NO MATCH FOUND',
        address: '',
        city: '',
        parcelId: ''
      });
      if ((i + 1) % 100 === 0) {
        console.log(`  [${i + 1}/${names.length}] ${originalName} - No matches`);
      }
      continue;
    }
    
    // Score each candidate
    const scored = candidates.map(c => {
      const conf = calculateConfidence(firstName, c.ownerName);
      const addr = addressByParcel[c.parcelId] || {};
      return {
        originalName,
        confidence: conf.tier,
        confidenceScore: conf.score,
        matchedOwner: c.ownerName,
        address: addr.address || '',
        city: addr.city || '',
        parcelId: c.parcelId
      };
    });
    
    // Filter to only HIGH and MEDIUM matches to reduce noise
    const goodMatches = scored.filter(s => s.confidence === 'HIGH' || s.confidence === 'MEDIUM');
    
    if (goodMatches.length > 0) {
      matchCount++;
      results.push(...goodMatches);
      if ((i + 1) % 100 === 0) {
        console.log(`  [${i + 1}/${names.length}] ${originalName} - ${goodMatches.length} matches`);
      }
    } else {
      // Include LOW matches only if there are few candidates (likely the right person)
      const lowMatches = scored.filter(s => s.confidence === 'LOW');
      if (lowMatches.length <= 3) {
        matchCount++;
        results.push(...lowMatches);
      } else {
        noMatchCount++;
        results.push({
          originalName,
          confidence: 'LOW',
          confidenceScore: 1,
          matchedOwner: `${lowMatches.length} LOW matches - review manually`,
          address: '',
          city: '',
          parcelId: ''
        });
      }
      if ((i + 1) % 100 === 0) {
        console.log(`  [${i + 1}/${names.length}] ${originalName} - ${lowMatches.length} LOW matches`);
      }
    }
  }
  
  // Sort by confidence
  results.sort((a, b) => (b.confidenceScore || 0) - (a.confidenceScore || 0));
  
  // Write output
  const headers = ['Original Name', 'Confidence', 'Matched Owner Name', 'Property Address', 'City', 'Parcel ID'];
  const outputLines = [headers.join(',')];
  
  for (const r of results) {
    outputLines.push([
      `"${r.originalName}"`,
      `"${r.confidence}"`,
      `"${r.matchedOwner}"`,
      `"${r.address}"`,
      `"${r.city}"`,
      `"${r.parcelId}"`
    ].join(','));
  }
  
  fs.writeFileSync(outputFile, outputLines.join('\n'));
  
  // Summary
  const highCount = results.filter(r => r.confidence === 'HIGH').length;
  const medCount = results.filter(r => r.confidence === 'MEDIUM').length;
  const lowCount = results.filter(r => r.confidence === 'LOW').length;
  
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('✅ Complete!');
  console.log(`   Names searched: ${names.length}`);
  console.log(`   With matches: ${matchCount}`);
  console.log(`   No matches: ${noMatchCount}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 Confidence Breakdown:');
  console.log(`   🟢 HIGH:   ${highCount} records`);
  console.log(`   🟡 MEDIUM: ${medCount} records`);
  console.log(`   🔴 LOW:    ${lowCount} records`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`   Total records: ${results.length}`);
  console.log(`   Output: ${outputFile}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
