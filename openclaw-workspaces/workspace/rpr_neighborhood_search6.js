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

    // Go directly to map search for the neighborhood
    await page.goto('https://www.narrpr.com/properties/search?q=Waters+Edge+Port+Orange+FL&searchType=neighborhood', { 
      waitUntil: 'domcontentloaded', timeout: 30000 
    });
    await page.waitForTimeout(5000);
    console.log('On map search:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map1.png', fullPage: false });

    // Click "Search in This Area" button
    const searchAreaBtn = await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Search in This Area')) {
          b.click();
          return 'clicked';
        }
      }
      return 'not found';
    });
    console.log('Search in This Area:', searchAreaBtn);
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map2.png', fullPage: false });

    // Check for property type filter - need to make sure it shows all types
    // First click "Property Type" dropdown using force to bypass header overlay
    await page.evaluate(() => {
      const labels = document.querySelectorAll('label');
      for (const l of labels) {
        if (l.textContent.trim() === 'Property Type') {
          l.click();
          return true;
        }
      }
      return false;
    });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map_proptype.png' });

    // Now click "All" in the property type dropdown
    await page.evaluate(() => {
      // Look for the "All" text in the property type dropdown area
      const spans = document.querySelectorAll('span, label, div');
      for (const s of spans) {
        if (s.textContent.trim() === 'All' && s.closest('[class*="property-type"], [class*="dropdown"], [class*="filter"]')) {
          s.click();
          return 'clicked All in dropdown';
        }
      }
      // Fallback: try clicking any element with text "All" near checkboxes
      const allLabels = document.querySelectorAll('label');
      for (const l of allLabels) {
        if (l.textContent.trim() === 'All') {
          l.click();
          return 'clicked All label';
        }
      }
      return 'not found';
    });
    console.log('Clicked All property types');
    await page.waitForTimeout(1000);

    // Close dropdown and search again
    await page.mouse.click(640, 400); // Click on map area
    await page.waitForTimeout(2000);

    // Click Search in This Area again
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Search in This Area')) {
          b.click();
          return;
        }
      }
    });
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map3.png', fullPage: false });
    
    // Get any result count or property data
    const pageContent = await page.evaluate(() => document.body.innerText.substring(0, 8000));
    console.log('\n--- MAP RESULTS ---\n', pageContent);

    // Try to look at map data layer / side panel
    const sidePanel = await page.$$eval('[class*="panel"], [class*="sidebar"], [class*="results"], [class*="list"]',
      els => els.map(e => e.innerText.substring(0, 500)).filter(t => t.length > 10).slice(0, 5)
    );
    console.log('\nSide panels:', JSON.stringify(sidePanel));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
