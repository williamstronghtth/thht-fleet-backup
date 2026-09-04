const { chromium } = require('playwright');

const PROPERTIES = [
  { address: '134 Deskin', city: 'South Daytona' },
  { address: '806 Silk Oak', city: 'New Smyrna' },
  { address: '1108 Loch Laggan', city: 'New Smyrna' }
];

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  // Accept disclaimer once
  await page.goto('https://vcpa.vcgov.org/search/real-property', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button, a');
    for (const btn of btns) {
      if (btn.textContent.trim() === 'Agree') btn.click();
    }
  });
  await page.waitForTimeout(2000);
  console.log('Accepted disclaimer\n');

  for (const prop of PROPERTIES) {
    console.log('='.repeat(60));
    console.log(`SEARCHING: ${prop.address}`);
    console.log('='.repeat(60));

    try {
      // Go to search
      await page.goto('https://vcpa.vcgov.org/search/real-property', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);

      // Search
      const input = await page.$('input[type="search"], input.form-control');
      if (input) {
        await input.type(prop.address, { delay: 60 });
        await page.waitForTimeout(4000);

        // Double-click first matching row
        const found = await page.evaluate((city) => {
          const rows = document.querySelectorAll('tbody tr');
          for (const row of rows) {
            const text = row.textContent.toUpperCase();
            if (text.includes(city.toUpperCase())) {
              row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
              return true;
            }
          }
          // Try first row if city not matched
          if (rows.length > 0) {
            rows[0].dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
            return true;
          }
          return false;
        }, prop.city);

        if (!found) {
          console.log('Property not found in search results');
          continue;
        }

        await page.waitForTimeout(5000);
        console.log('Property URL:', page.url());

        // Click Permits tab
        try {
          await page.locator('text=Permits').first().click();
          await page.waitForTimeout(3000);
        } catch (e) {
          console.log('Could not click Permits tab');
          continue;
        }

        // Extract permits
        const content = await page.evaluate(() => document.body.innerText);
        
        // Find permit section
        const lines = content.split('\n');
        let inPermits = false;
        let permits = [];
        
        for (const line of lines) {
          if (line.includes('Date') && line.includes('Number') && line.includes('Description')) {
            inPermits = true;
            continue;
          }
          if (inPermits && line.trim().length > 0) {
            // Check if it looks like a permit line (starts with date pattern)
            if (line.match(/^\d{2}\/\d{2}\/\d{4}/)) {
              permits.push(line.trim());
            } else if (line.includes('Home') || line.includes('123 W.')) {
              break;
            }
          }
        }

        console.log('\nPERMITS FOUND:');
        if (permits.length === 0) {
          console.log('No permits found');
        } else {
          permits.forEach(p => console.log(p));
        }
        console.log('');
      }
    } catch (err) {
      console.log('Error:', err.message);
    }
  }

  await browser.close();
})();
