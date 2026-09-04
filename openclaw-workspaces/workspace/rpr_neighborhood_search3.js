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

    // Search for the neighborhood
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    await searchInput.click();
    await searchInput.fill('');
    await searchInput.type(NEIGHBORHOOD, { delay: 80 });
    await page.waitForTimeout(4000);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(6000);
    console.log('Search results URL:', page.url());

    // Step 1: Click Type/Status to open that dropdown
    const typeStatusBtn = await page.$('text=Type/Status');
    if (typeStatusBtn) {
      await typeStatusBtn.click();
      await page.waitForTimeout(2000);
      console.log('Opened Type/Status dropdown');

      // Click "Public Records" label/checkbox
      const prLabel = await page.$('label:has-text("Public Records"), text=Public Records');
      if (prLabel) {
        await prLabel.click();
        console.log('Clicked Public Records');
        await page.waitForTimeout(1000);
      }

      // Close dropdown by clicking elsewhere
      await page.click('body', { position: { x: 640, y: 50 } });
      await page.waitForTimeout(1000);
    }

    // Step 2: Click Property Type to open that dropdown  
    const propTypeBtn = await page.locator('text=Property Type').first();
    await propTypeBtn.click();
    await page.waitForTimeout(2000);
    console.log('Opened Property Type dropdown');

    // Click "All" to select all property types
    // Look for the "All" option within the dropdown
    const allOption = await page.locator('label:has-text("All"), text=All').first();
    if (allOption) {
      await allOption.click();
      console.log('Clicked "All" property types');
      await page.waitForTimeout(1000);
    }

    // Close dropdown
    await page.click('body', { position: { x: 640, y: 50 } });
    await page.waitForTimeout(4000);

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_waters_edge.png' });
    console.log('Screenshot saved');

    // Get results
    const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
    console.log('\n--- PAGE CONTENT ---\n', content);

    // Check if there are property cards or result count
    const resultCount = await page.$eval('[class*="result-count"], [class*="ResultCount"], [class*="total"]', el => el.textContent).catch(() => 'not found');
    console.log('Result count element:', resultCount);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
