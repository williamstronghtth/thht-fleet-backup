const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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

    // Go to map search for Port Orange
    await page.goto('https://www.narrpr.com/properties/search?scid=261967480', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('On map search page');

    // Click "Show Geographies" to see neighborhoods
    const showGeo = await page.$('button:has-text("Show Geographies"), a:has-text("Show Geographies"), [class*="geograph"]');
    if (showGeo) {
      await showGeo.click();
      await page.waitForTimeout(2000);
      console.log('Clicked Show Geographies');
      
      // Get the dropdown content
      const geoContent = await page.evaluate(() => {
        const els = document.querySelectorAll('[class*="dropdown"], [class*="menu"], [class*="panel"], [role="menu"], [role="listbox"]');
        return Array.from(els).map(e => e.innerText.substring(0, 500)).join('\n---\n');
      });
      console.log('Geography options:', geoContent);
    }

    // Try clicking More Filters to set Time Owned
    const moreFilters = await page.$('button:has-text("More Filters")');
    if (moreFilters) {
      await moreFilters.click();
      await page.waitForTimeout(3000);
      console.log('\nClicked More Filters');
      
      // Get all the filter content
      const filterContent = await page.evaluate(() => document.body.innerText);
      
      // Extract just the filter section
      const filterStart = filterContent.indexOf('More Filters');
      const relevantContent = filterContent.substring(filterStart, filterStart + 4000);
      console.log('Filter section:', relevantContent);
    }

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_filters.png' });
    console.log('\nScreenshot saved');

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
