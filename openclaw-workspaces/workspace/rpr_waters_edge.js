const { chromium } = require('playwright');

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

    // Step 1: Go to home, search for "Port Orange, FL" to get to the right area
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    await searchInput.click();
    await searchInput.fill('');
    await searchInput.type('Port Orange, FL', { delay: 80 });
    await page.waitForTimeout(4000);
    
    // Look for Port Orange suggestion in autocomplete
    const suggestions = await page.evaluate(() => {
      const items = document.querySelectorAll('[role="option"], [class*="suggestion"], [class*="autocomplete"] li, [class*="dropdown-item"]');
      return Array.from(items).map(e => e.textContent.trim()).slice(0, 10);
    });
    console.log('Suggestions for Port Orange:', suggestions);

    // Try to click on Port Orange suggestion
    const clicked = await page.evaluate(() => {
      const items = document.querySelectorAll('[role="option"], [class*="suggestion"], [class*="autocomplete"] li, [class*="dropdown-item"], [class*="keyboard-nav"]');
      for (const item of items) {
        const text = item.textContent.trim().toLowerCase();
        if (text.includes('port orange') && !text.includes('listing') && !text.includes('apn')) {
          item.click();
          return item.textContent.trim();
        }
      }
      return null;
    });

    if (clicked) {
      console.log('Clicked suggestion:', clicked);
    } else {
      // Press Enter
      await page.keyboard.press('Enter');
      console.log('Pressed Enter for Port Orange');
    }

    await page.waitForTimeout(6000);
    console.log('After Port Orange search:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po1.png' });

    // Now we should be on the map search near Port Orange
    // Check if this is the map view
    const content1 = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('Page content:', content1.substring(0, 500));

    // Step 2: Now use "Show Geographies" to see neighborhood boundaries
    const showGeoClicked = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const b of btns) {
        if (b.textContent.includes('Show Geographies')) {
          b.click();
          return 'clicked';
        }
      }
      return 'not found';
    });
    console.log('Show Geographies:', showGeoClicked);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po2.png' });

    // Check what geography options are available
    const geoContent = await page.evaluate(() => document.body.innerText.substring(0, 5000));
    console.log('After Show Geographies:', geoContent.substring(0, 1000));

    // Look for "Neighborhoods" option in the geography panel
    const nbhClicked = await page.evaluate(() => {
      const els = document.querySelectorAll('button, a, label, span, div');
      for (const e of els) {
        const text = e.textContent.trim();
        if (text === 'Neighborhoods' || text === 'Subdivision') {
          e.click();
          return text;
        }
      }
      return 'not found';
    });
    console.log('Neighborhoods option:', nbhClicked);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po3.png' });

    // Step 3: Now try searching within the location field for Waters Edge specifically
    // Clear and re-search
    const locInput = await page.$('.location-input, input[placeholder*="Location"], input[placeholder*="location"]');
    if (locInput) {
      await locInput.click({ clickCount: 3 });
      await locInput.fill('');
      await locInput.type('Waters Edge, Port Orange, FL', { delay: 80 });
      await page.waitForTimeout(4000);
      
      const suggestions2 = await page.evaluate(() => {
        const items = document.querySelectorAll('[role="option"], [class*="suggestion"], [class*="autocomplete"] li, [class*="dropdown-item"], [class*="keyboard-nav"]');
        return Array.from(items).map(e => ({ text: e.textContent.trim(), class: e.className.substring(0, 60) })).slice(0, 10);
      });
      console.log('Waters Edge suggestions:', JSON.stringify(suggestions2));
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po4.png' });
    }

    // Final full page content
    const finalContent = await page.evaluate(() => document.body.innerText.substring(0, 8000));
    console.log('\n--- FINAL ---\n', finalContent);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
