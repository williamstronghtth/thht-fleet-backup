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

    // Go directly to Map Search
    await page.goto('https://www.narrpr.com/map', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('Map URL:', page.url());
    
    // If redirected to a different page, try the map search link from research menu
    if (!page.url().includes('map')) {
      // Try Research > Map Search path
      await page.goto('https://www.narrpr.com/properties/map', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      console.log('Map URL attempt 2:', page.url());
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map_home.png' });
    
    // Find the location/search input on the map page
    const allInputs = await page.$$eval('input:visible', els => els.map(e => ({
      type: e.type, placeholder: e.placeholder, id: e.id, name: e.name, 
      class: e.className.substring(0, 60), value: e.value
    })));
    console.log('All visible inputs:', JSON.stringify(allInputs, null, 2));

    // Try to find the location search input
    let locInput = await page.$('.location-input:visible');
    if (!locInput) locInput = await page.$('input[placeholder*="Location"]:visible, input[placeholder*="location"]:visible, input[placeholder*="Address"]:visible, input[placeholder*="Search"]:visible, input[placeholder*="search"]:visible');
    if (!locInput) locInput = await page.$('input[type="text"]:visible');

    if (locInput) {
      // Search for a known address in Waters Edge, Port Orange
      // Waters Edge is a subdivision off Taylor Road in Port Orange
      await locInput.click({ clickCount: 3 });
      await locInput.fill('');
      await locInput.type('Waters Edge Dr, Port Orange, FL', { delay: 80 });
      await page.waitForTimeout(4000);
      
      const suggestions = await page.evaluate(() => {
        const items = document.querySelectorAll('[role="option"], [class*="suggestion"] li, [class*="autocomplete"] li, [class*="keyboard-nav-suggestion"]');
        return Array.from(items).map(e => e.textContent.trim()).slice(0, 10);
      });
      console.log('Suggestions:', suggestions);

      // Click first relevant suggestion or press Enter
      const clickedSugg = await page.evaluate(() => {
        const items = document.querySelectorAll('[role="option"], [class*="suggestion"], [class*="keyboard-nav-suggestion"]');
        for (const item of items) {
          const text = item.textContent.toLowerCase();
          if (text.includes('waters edge') || text.includes('port orange')) {
            item.click();
            return item.textContent.trim();
          }
        }
        return null;
      });
      
      if (clickedSugg) {
        console.log('Clicked:', clickedSugg);
      } else {
        await page.keyboard.press('Enter');
        console.log('Pressed Enter');
      }
      
      await page.waitForTimeout(6000);
    }

    console.log('Current URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_waters_edge_map.png' });
    
    // Check buttons available
    const buttons = await page.$$eval('button:visible', els => 
      els.map(e => e.textContent.trim()).filter(t => t.length > 0 && t.length < 50)
    );
    console.log('Visible buttons:', buttons);
    
    // Try to click "Map Search" or "Search in This Area"
    const searchAreaResult = await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        const text = b.textContent.trim();
        if (text.includes('Search in This Area') || text === 'Map Search') {
          b.click();
          return text;
        }
      }
      return 'not found';
    });
    console.log('Clicked:', searchAreaResult);
    await page.waitForTimeout(5000);

    // Show Geographies
    const geoResult = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const b of btns) {
        if (b.textContent.includes('Show Geographies')) {
          b.click();
          return 'clicked';
        }
      }
      return 'not found';
    });
    console.log('Show Geographies:', geoResult);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_geographies.png' });
    
    // Get page content
    const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
    console.log('\n--- CONTENT ---\n', content);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
