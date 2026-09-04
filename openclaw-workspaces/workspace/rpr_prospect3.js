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
    console.log('Logged in');

    // Go to map search for Port Orange
    await page.goto('https://www.narrpr.com/properties/search?scid=261967480', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('On map search');

    // Click "More Filters" - try by the icon/button with filter icon
    // It might be a mat-icon or similar
    const allButtons = await page.$$eval('button, [role="button"]', els => els.map(e => ({
      text: e.textContent.trim().substring(0, 50),
      class: e.className.substring(0, 80),
      id: e.id
    })));
    console.log('All buttons:', JSON.stringify(allButtons, null, 2));

    // Try clicking More Filters by various methods
    await page.click('text=More Filters').catch(() => console.log('text=More Filters not found'));
    await page.waitForTimeout(1000);
    
    // Try finding it as a clickable element
    const moreFiltersEl = await page.locator(':text("More Filters")').first();
    if (moreFiltersEl) {
      try {
        await moreFiltersEl.click();
        console.log('Clicked More Filters via locator');
        await page.waitForTimeout(3000);
      } catch(e) {
        console.log('Could not click More Filters locator');
      }
    }

    // Try the Type/Status dropdown
    console.log('\nTrying Type/Status...');
    await page.click('text=Type/Status').catch(() => console.log('Type/Status not found'));
    await page.waitForTimeout(2000);
    
    let bodyText = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('After Type/Status click:', bodyText.substring(0, 2000));

    // Screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_prospect3.png', fullPage: true });
    console.log('\nScreenshot saved');
    
    // Now try a more targeted approach - search for a specific neighborhood
    console.log('\n--- Trying neighborhood search ---');
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (searchInput) {
      await searchInput.click({ clickCount: 3 }); // select all
      await searchInput.type('Spruce Creek, Port Orange, FL', { delay: 50 });
      await page.waitForTimeout(3000);
      
      const suggestions = await page.$$eval('[role="option"], [class*="suggestion"] li, [class*="autocomplete"] li', 
        els => els.map(e => e.textContent.trim()).slice(0, 10));
      console.log('Suggestions:', suggestions);
      
      if (suggestions.length > 0) {
        const firstOpt = await page.$('[role="option"]:first-child');
        if (firstOpt) {
          await firstOpt.click();
          console.log('Clicked first suggestion');
        }
      } else {
        await page.keyboard.press('Enter');
      }
      
      await page.waitForTimeout(5000);
      bodyText = await page.evaluate(() => document.body.innerText.substring(0, 4000));
      console.log('After neighborhood search:', bodyText);
    }

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_neighborhood.png', fullPage: true });

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
