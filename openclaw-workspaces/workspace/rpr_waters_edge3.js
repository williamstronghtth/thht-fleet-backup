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

    // Search for a specific address in Waters Edge to pin the map location
    // Try "1 Waters Edge Dr, Port Orange, FL" or similar
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    const searchInput = await page.$('input[type="text"]:visible');
    await searchInput.click();
    await searchInput.fill('');
    // Search for the subdivision name in RPR's property search  
    await searchInput.type('Waters Edge Port Orange FL 32128', { delay: 60 });
    await page.waitForTimeout(4000);

    // Get autocomplete suggestions
    const suggestions = await page.evaluate(() => {
      const container = document.querySelector('[class*="suggestion"], [class*="autocomplete"], [class*="dropdown"]');
      if (container) return container.innerText;
      return 'no suggestions container found';
    });
    console.log('Suggestions text:', suggestions);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_we3_suggestions.png' });

    // Press Enter to search
    await page.keyboard.press('Enter');
    await page.waitForTimeout(6000);
    console.log('Search result URL:', page.url());

    // Now try switching to Map view by clicking the map icon
    const mapViewClicked = await page.evaluate(() => {
      // Look for map view toggle icons - usually the third icon in view options
      const icons = document.querySelectorAll('[class*="view-toggle"] button, [class*="view-option"], [aria-label*="map"], [title*="map"], [title*="Map"]');
      for (const icon of icons) {
        if (icon.title?.toLowerCase().includes('map') || icon.getAttribute('aria-label')?.toLowerCase().includes('map')) {
          icon.click();
          return 'clicked map view: ' + (icon.title || icon.getAttribute('aria-label'));
        }
      }
      // Try finding by class patterns
      const allBtns = document.querySelectorAll('button');
      for (const b of allBtns) {
        const cls = b.className;
        if (cls.includes('map') || cls.includes('Map')) {
          b.click();
          return 'clicked by class: ' + cls.substring(0, 50);
        }
      }
      // Try the third button in a group that looks like view toggles
      const btnGroups = document.querySelectorAll('[class*="btn-group"], [class*="button-group"], [class*="toggle-group"]');
      for (const group of btnGroups) {
        const btns = group.querySelectorAll('button');
        if (btns.length >= 3) {
          btns[2].click();
          return 'clicked 3rd in group';
        }
      }
      return 'not found';
    });
    console.log('Map view toggle:', mapViewClicked);
    await page.waitForTimeout(5000);
    console.log('After map toggle URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_we3_map.png' });

    // Get page content to see what we're looking at
    const content = await page.evaluate(() => document.body.innerText.substring(0, 6000));
    console.log('\n--- CONTENT ---\n', content.substring(0, 2000));

    // Check for "Show Geographies" button now
    const allButtonTexts = await page.$$eval('button:visible', els => 
      els.map(e => ({ text: e.textContent.trim(), class: e.className.substring(0, 40) })).filter(e => e.text.length > 0)
    );
    console.log('\nAll buttons:', JSON.stringify(allButtonTexts));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
