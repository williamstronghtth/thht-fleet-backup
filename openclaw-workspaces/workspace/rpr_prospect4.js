const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
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

    // Go to map search
    await page.goto('https://www.narrpr.com/properties/search', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);

    // Search for Spruce Creek neighborhood
    const searchInput = await page.$('input[type="text"]:visible');
    if (searchInput) {
      await searchInput.click({ clickCount: 3 });
      await searchInput.type('Spruce Creek, Port Orange, FL', { delay: 50 });
      await page.waitForTimeout(3000);
      
      // Click on "Samsula-Spruce Creek, Florida" in Places
      const placeOption = await page.locator('text=Samsula-Spruce Creek').first();
      try {
        await placeOption.click();
        console.log('Clicked Samsula-Spruce Creek');
        await page.waitForTimeout(5000);
      } catch(e) {
        console.log('Could not click place, trying Streets option');
        const streetOption = await page.locator('text=Spruce Crk').first();
        try {
          await streetOption.click();
          console.log('Clicked Spruce Crk street');
          await page.waitForTimeout(5000);
        } catch(e2) {
          await page.keyboard.press('Enter');
          await page.waitForTimeout(5000);
        }
      }
    }

    console.log('URL after search:', page.url());

    // Now click More Filters button (the filter icon button)
    const filterBtn = await page.$('button.filter-button, button:has-text("More Filters")');
    if (filterBtn) {
      await filterBtn.click();
      await page.waitForTimeout(3000);
      console.log('Opened More Filters');
    }

    // Get full page text to see all available filters
    const fullText = await page.evaluate(() => document.body.innerText);
    console.log('Full page text (first 6000 chars):', fullText.substring(0, 6000));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_spruce_creek.png', fullPage: true });
    console.log('\nScreenshot saved');

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
