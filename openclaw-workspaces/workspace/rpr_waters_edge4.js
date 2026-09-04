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

    // Step 1: Search Port Orange, FL from home
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    const searchInput = await page.$('input[type="text"]:visible');
    await searchInput.click();
    await searchInput.type('Port Orange, FL', { delay: 60 });
    await page.waitForTimeout(3000);

    // Click Port Orange suggestion
    await page.evaluate(() => {
      const items = document.querySelectorAll('[class*="keyboard-nav-suggestion"]');
      for (const item of items) {
        if (item.textContent.includes('Port Orange')) {
          item.click();
          return;
        }
      }
    });
    await page.waitForTimeout(6000);
    console.log('Port Orange search done:', page.url());

    // Step 2: Switch to Map view
    const mapBtnClicked = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, [role="button"]');
      for (const b of btns) {
        if (b.title === 'Map View' || b.getAttribute('aria-label') === 'Map View') {
          b.click();
          return 'clicked by title/aria';
        }
      }
      // Try icon buttons - look for the 3rd toggle icon
      const toggles = document.querySelectorAll('[class*="view-toggle"] button, [class*="ViewToggle"] button');
      if (toggles.length >= 3) {
        toggles[2].click();
        return 'clicked 3rd toggle';
      }
      // Try finding map icon via SVG or img
      const allBtns = document.querySelectorAll('button');
      for (const b of allBtns) {
        const cls = b.className + ' ' + b.innerHTML;
        if (cls.includes('map-view') || cls.includes('mapView') || cls.includes('fa-map')) {
          b.click();
          return 'clicked by map class: ' + b.className.substring(0, 30);
        }
      }
      return 'not found';
    });
    console.log('Map view switch:', mapBtnClicked);
    await page.waitForTimeout(5000);
    console.log('After map switch URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po_map.png' });

    // Verify we're on map search
    const hasMapControls = await page.evaluate(() => {
      const text = document.body.innerText;
      return text.includes('Show Geographies') || text.includes('Search in This Area');
    });
    console.log('Has map controls:', hasMapControls);

    if (!hasMapControls) {
      // Try clicking map icon differently - look for the fa-map or map icon
      console.log('Trying alternate map view approach...');
      const allBtnInfo = await page.$$eval('button:visible', els => 
        els.map(e => ({ text: e.textContent.trim(), title: e.title, class: e.className.substring(0, 50), ariaLabel: e.getAttribute('aria-label') }))
          .filter(e => e.text || e.title || e.ariaLabel)
      );
      console.log('All visible buttons:', JSON.stringify(allBtnInfo.slice(0, 20), null, 2));
    }

    // Step 3: Click "Show Geographies"
    if (hasMapControls) {
      await page.evaluate(() => {
        const btns = document.querySelectorAll('button');
        for (const b of btns) {
          if (b.textContent.trim() === 'Show Geographies') {
            b.click();
            return;
          }
        }
      });
      console.log('Clicked Show Geographies');
      await page.waitForTimeout(3000);
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_po_geo.png' });

      // Get the geography options
      const geoContent = await page.evaluate(() => document.body.innerText.substring(0, 6000));
      console.log('\n--- After Geographies ---\n', geoContent.substring(0, 2000));

      // Look for Subdivision/Neighborhood options
      const geoOptions = await page.$$eval('[class*="geo"] button, [class*="geo"] label, [class*="geo"] a, [class*="geography"] *, [class*="panel"] label, [class*="panel"] button', 
        els => els.map(e => e.textContent.trim()).filter(t => t.length > 0 && t.length < 50).slice(0, 20)
      );
      console.log('Geography options:', geoOptions);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
