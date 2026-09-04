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
    console.log('Logged in:', page.url());

    // Navigate to Research > Map Search
    console.log('\nNavigating to Map Search...');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Look for Research menu or Map Search link
    const researchLink = await page.$('a:has-text("Research"), button:has-text("Research")');
    if (researchLink) {
      await researchLink.click();
      await page.waitForTimeout(2000);
      console.log('Clicked Research');
    }
    
    // Look for Map Search
    const mapSearchLink = await page.$('a:has-text("Map Search")');
    if (mapSearchLink) {
      await mapSearchLink.click();
      await page.waitForTimeout(3000);
      console.log('Clicked Map Search');
    }
    
    console.log('Current URL:', page.url());

    // Search for Port Orange FL
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type('Port Orange, FL', { delay: 50 });
      console.log('Typed Port Orange, FL');
      await page.waitForTimeout(3000);
      
      // Click first suggestion
      const suggestion = await page.$('[role="option"]:first-child, [class*="suggestion"]:first-child');
      if (suggestion) {
        await suggestion.click();
        console.log('Clicked suggestion');
      } else {
        await page.keyboard.press('Enter');
        console.log('Pressed enter');
      }
      await page.waitForTimeout(5000);
    }

    console.log('After search URL:', page.url());
    
    // Now look for Type/Status filter to set Public Record
    console.log('\nLooking for filters...');
    const typeStatusBtn = await page.$('button:has-text("Type/Status"), [class*="filter"]:has-text("Type/Status")');
    if (typeStatusBtn) {
      await typeStatusBtn.click();
      await page.waitForTimeout(2000);
      console.log('Clicked Type/Status');
      
      // Look for Public Record option
      const publicRecord = await page.$('text=Public Record, label:has-text("Public Record"), [class*="option"]:has-text("Public Record")');
      if (publicRecord) {
        await publicRecord.click();
        console.log('Selected Public Record');
        await page.waitForTimeout(2000);
      }
    }

    // Look for More Filters
    const moreFilters = await page.$('button:has-text("More Filters"), a:has-text("More Filters")');
    if (moreFilters) {
      await moreFilters.click();
      await page.waitForTimeout(3000);
      console.log('Clicked More Filters');
      
      // Get visible text to understand the filter options
      const filterText = await page.evaluate(() => document.body.innerText.substring(0, 5000));
      console.log('Filter options:', filterText);
    }

    // Take a screenshot of what we see
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_prospect_screen.png' });
    console.log('Screenshot saved');

    // Get full page content
    const content = await page.evaluate(() => document.body.innerText.substring(0, 6000));
    console.log('\nPage content:', content);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
