const { chromium } = require('playwright');

const NEIGHBORHOOD = 'Waters Edge, Port Orange, FL';

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    // Login
    console.log('Logging in...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in');

    // Go to search and find neighborhood
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    await searchInput.click();
    await searchInput.fill('');
    await searchInput.type(NEIGHBORHOOD, { delay: 80 });
    await page.waitForTimeout(4000);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(6000);
    console.log('Search URL:', page.url());

    // Screenshot the initial state
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_ne_initial.png' });

    // Open Type/Status dropdown and make sure Public Records is selected
    await page.locator('text=Type/Status').first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_ne_typestatus.png' });

    // Find checkboxes in the dropdown and their labels
    const typeStatusInfo = await page.evaluate(() => {
      // Find the dropdown that's currently open
      const labels = document.querySelectorAll('label');
      const results = [];
      labels.forEach(l => {
        const input = l.querySelector('input[type="checkbox"]');
        if (input) {
          results.push({
            text: l.textContent.trim(),
            checked: input.checked,
            id: input.id,
            name: input.name
          });
        }
      });
      return results;
    });
    console.log('Type/Status checkboxes:', JSON.stringify(typeStatusInfo, null, 2));

    // Make sure "Public Records" is checked - find by evaluating
    const publicRecChecked = await page.evaluate(() => {
      const labels = document.querySelectorAll('label');
      for (const l of labels) {
        if (l.textContent.trim() === 'Public Records') {
          const input = l.querySelector('input[type="checkbox"]');
          if (input && !input.checked) {
            l.click();
            return 'clicked to check';
          }
          return input ? 'already checked' : 'no input found';
        }
      }
      return 'label not found';
    });
    console.log('Public Records:', publicRecChecked);
    await page.waitForTimeout(1000);

    // Close Type/Status dropdown by clicking header area
    await page.mouse.click(640, 50);
    await page.waitForTimeout(2000);

    // Now handle Property Type - click to open
    await page.locator('text=Property Type').first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_ne_proptype.png' });

    // Click "All" checkbox to select all property types
    const allClicked = await page.evaluate(() => {
      const labels = document.querySelectorAll('label');
      for (const l of labels) {
        const text = l.textContent.trim();
        if (text === 'All') {
          const input = l.querySelector('input[type="checkbox"]');
          if (input && !input.checked) {
            l.click();
            return 'clicked All';
          }
          return input ? 'All already checked' : 'no input';
        }
      }
      return 'All label not found';
    });
    console.log('Property Type All:', allClicked);
    await page.waitForTimeout(1000);

    // Close dropdown
    await page.mouse.click(640, 50);
    await page.waitForTimeout(5000);

    // Final screenshot and content
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_ne_results.png' });
    const content = await page.evaluate(() => document.body.innerText.substring(0, 10000));
    console.log('\n--- RESULTS ---\n', content);

    // If we see results, try to get the property list
    const propertyCards = await page.$$eval('[class*="property-card"], [class*="PropertyCard"], [class*="result-item"], [class*="search-result"], tr[class*="prop"], [class*="property-row"]',
      els => els.map(e => e.textContent.trim().substring(0, 200)).slice(0, 20)
    );
    console.log('\nProperty cards found:', propertyCards.length);
    propertyCards.forEach((c, i) => console.log(`  ${i+1}: ${c}`));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
