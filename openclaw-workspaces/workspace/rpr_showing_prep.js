const { chromium } = require('playwright');

const PROPERTIES = [
  '134 Deskin Dr, South Daytona, FL 32119',
  '806 Silk Oak Ct, New Smyrna Beach, FL 32168',
  '1108 Loch Laggan Ct, New Smyrna Beach, FL 32168'
];

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    // Login
    console.log('Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in!\n');

    for (let i = 0; i < PROPERTIES.length; i++) {
      const addr = PROPERTIES[i];
      console.log(`\n${'='.repeat(60)}`);
      console.log(`PROPERTY ${i+1}: ${addr}`);
      console.log('='.repeat(60));

      // Go to home and search
      await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);

      const searchInput = await page.$('input[type="text"]:visible');
      if (searchInput) {
        await searchInput.click();
        await searchInput.fill('');
        await searchInput.type(addr, { delay: 40 });
        await page.waitForTimeout(3000);

        // Click first suggestion
        await page.evaluate(() => {
          const items = document.querySelectorAll('[class*="keyboard-nav-suggestion"]');
          for (const item of items) {
            if (!item.textContent.includes('listing ID') && !item.textContent.includes('APN')) {
              item.click();
              return;
            }
          }
        });
        await page.waitForTimeout(6000);
        console.log('URL:', page.url());

        // Get page content - look for property details
        const content = await page.evaluate(() => {
          const text = document.body.innerText;
          return text.substring(0, 12000);
        });

        // Extract key info
        const lines = content.split('\n').filter(l => l.trim().length > 0);
        
        // Look for specific data points
        let inPropertySection = false;
        let relevantLines = [];
        
        for (const line of lines) {
          const l = line.trim();
          // Skip navigation/header stuff
          if (l.includes('Site Navigation') || l.includes('My Work') || l.includes('Terms') || l.includes('Report a map error')) continue;
          if (l.length < 3) continue;
          
          // Capture property-related info
          if (l.includes('RVM') || l.includes('Value') || l.includes('Bed') || l.includes('Bath') || 
              l.includes('Sq Ft') || l.includes('sqft') || l.includes('Year Built') || l.includes('Lot') ||
              l.includes('List Price') || l.includes('DOM') || l.includes('Days') || l.includes('Owner') ||
              l.includes('Sale') || l.includes('Sold') || l.includes('Price') || l.includes('Status') ||
              l.includes('Type') || l.includes('Pool') || l.includes('Garage') || l.includes('Built') ||
              l.includes('Acres') || l.includes('Tax') || l.includes('Zoning') || l.includes('HOA') ||
              l.includes('School') || l.includes('Walk') || l.match(/^\$[\d,]+/) || l.match(/^\d{1,2}\/\d{1,2}\/\d{2,4}/)) {
            relevantLines.push(l);
          }
        }
        
        console.log('\n--- KEY DATA ---');
        // Dedupe and print
        const seen = new Set();
        for (const line of relevantLines.slice(0, 40)) {
          if (!seen.has(line)) {
            seen.add(line);
            console.log(line);
          }
        }
        
        // Also grab the full first 2000 chars for context
        console.log('\n--- RAW EXCERPT ---');
        console.log(content.substring(0, 2500));
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
