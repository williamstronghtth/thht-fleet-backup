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

    // Step 1: Search Port Orange, FL
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    const searchInput = await page.$('input[type="text"]:visible');
    await searchInput.click();
    await searchInput.type('Port Orange, FL', { delay: 60 });
    await page.waitForTimeout(3000);
    await page.evaluate(() => {
      const items = document.querySelectorAll('[class*="keyboard-nav-suggestion"]');
      for (const item of items) {
        if (item.textContent.includes('Port Orange')) { item.click(); return; }
      }
    });
    await page.waitForTimeout(6000);
    console.log('Searched Port Orange');

    // Step 2: Switch to Map view
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.title === 'Map View') { b.click(); return; }
      }
    });
    await page.waitForTimeout(5000);
    console.log('Switched to map view');

    // Step 3: Click Show Geographies
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.trim() === 'Show Geographies') { b.click(); return; }
      }
    });
    await page.waitForTimeout(2000);
    console.log('Opened geographies');

    // Step 4: Click "Micro Neighborhoods" 
    await page.evaluate(() => {
      const items = document.querySelectorAll('button, a, li, span');
      for (const item of items) {
        if (item.textContent.trim() === 'Micro Neighborhoods') { item.click(); return; }
      }
    });
    await page.waitForTimeout(5000);
    console.log('Clicked Micro Neighborhoods');
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_micro_nbh.png' });

    // Check if neighborhood names/labels are visible on the map or in a list
    const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
    
    // Look for "Waters Edge" in the page content
    if (content.toLowerCase().includes('waters edge')) {
      console.log('Found "Waters Edge" in page content!');
    } else {
      console.log('Waters Edge not visible in text content');
    }
    
    // Check for any neighborhood labels/list that appeared
    const nbhLabels = await page.$$eval('[class*="label"], [class*="marker"], [class*="tooltip"], [class*="overlay"]', 
      els => els.map(e => e.textContent.trim()).filter(t => t.length > 2 && t.length < 50).slice(0, 30)
    );
    console.log('Labels on map:', nbhLabels);

    // Try to zoom in more — the map might need to be zoomed to see micro neighborhoods
    // Zoom in by clicking the + button or using keyboard
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() => {
        const zoomIn = document.querySelector('[aria-label="Zoom in"], [title="Zoom in"]');
        if (zoomIn) zoomIn.click();
      });
      await page.waitForTimeout(2000);
    }
    console.log('Zoomed in 3x');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_micro_zoomed.png' });

    // Check for neighborhood labels again after zoom
    const labelsAfterZoom = await page.evaluate(() => {
      const text = document.body.innerText;
      // Look for any text that might be neighborhood names
      const lines = text.split('\n').filter(l => l.trim().length > 0 && l.trim().length < 50);
      return lines.slice(0, 50);
    });
    console.log('Text lines after zoom:', labelsAfterZoom);

    // Try Minor Neighborhoods instead
    console.log('\n--- Trying Minor Neighborhoods ---');
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.trim() === 'Show Geographies') { b.click(); return; }
      }
    });
    await page.waitForTimeout(1000);
    await page.evaluate(() => {
      const items = document.querySelectorAll('button, a, li, span');
      for (const item of items) {
        if (item.textContent.trim() === 'Minor Neighborhoods') { item.click(); return; }
      }
    });
    await page.waitForTimeout(5000);
    console.log('Clicked Minor Neighborhoods');
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_minor_nbh.png' });

    const contentMinor = await page.evaluate(() => document.body.innerText.substring(0, 5000));
    console.log('Content after minor:', contentMinor.substring(0, 1000));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
