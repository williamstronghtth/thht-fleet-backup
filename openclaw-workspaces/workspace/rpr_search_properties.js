const { chromium } = require('playwright');

const ADDRESSES = [
  '134 Deskin Dr, South Daytona, FL 32119',
  '785 Falcon Dr, Port Orange, FL 32127',
  '806 Silk Oak Ct, New Smyrna Beach, FL 32168',
  '1108 Loch Laggan Ct, New Smyrna Beach, FL 32168'
];

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    // Login first
    console.log('Logging in...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in. URL:', page.url());

    // Search each property
    for (let i = 0; i < ADDRESSES.length; i++) {
      const addr = ADDRESSES[i];
      console.log(`\n========================================`);
      console.log(`PROPERTY ${i+1}: ${addr}`);
      console.log(`========================================`);

      // Go to home page
      await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Find and use the search bar
      const searchInput = await page.$('input[type="search"], input[placeholder*="Search"], input[placeholder*="search"], input[placeholder*="Address"], input[aria-label*="search"], input[aria-label*="Search"]');
      
      if (!searchInput) {
        // Try finding any prominent input
        const allInputs = await page.$$('input:visible');
        console.log(`Found ${allInputs.length} visible inputs`);
        for (const inp of allInputs) {
          const attrs = await inp.evaluate(e => ({ type: e.type, placeholder: e.placeholder, id: e.id, class: e.className }));
          console.log('Input:', JSON.stringify(attrs));
        }
        
        // Try clicking on search area
        const searchArea = await page.$('[class*="search"], [class*="Search"]');
        if (searchArea) {
          await searchArea.click();
          await page.waitForTimeout(1000);
        }
      }

      // Try the global search - RPR usually has a search bar at the top
      const topSearch = await page.$('input[type="text"]:visible, input[type="search"]:visible');
      if (topSearch) {
        await topSearch.click();
        await topSearch.fill('');
        await topSearch.type(addr, { delay: 50 });
        console.log('Typed address in search');
        await page.waitForTimeout(3000);
        
        // Look for autocomplete suggestions
        const suggestions = await page.$$eval('[class*="suggestion"], [class*="autocomplete"], [class*="dropdown"] li, [class*="result"] li, [role="option"], [role="listbox"] [role="option"]', 
          els => els.map(e => e.textContent.trim()).slice(0, 5));
        console.log('Suggestions:', suggestions);

        // Click first suggestion or press enter
        if (suggestions.length > 0) {
          const firstSuggestion = await page.$('[class*="suggestion"]:first-child, [class*="autocomplete"] li:first-child, [role="option"]:first-child, [role="listbox"] [role="option"]:first-child');
          if (firstSuggestion) {
            await firstSuggestion.click();
            console.log('Clicked first suggestion');
          } else {
            await page.keyboard.press('Enter');
          }
        } else {
          await page.keyboard.press('Enter');
        }
        
        await page.waitForTimeout(5000);
        console.log('Result URL:', page.url());
        
        // Get page content
        const content = await page.evaluate(() => document.body.innerText.substring(0, 4000));
        console.log('Content:', content);
      } else {
        console.log('No search input found on page');
        // Try direct URL approach
        const encodedAddr = encodeURIComponent(addr);
        await page.goto(`https://www.narrpr.com/search?q=${encodedAddr}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
        await page.waitForTimeout(5000);
        const content = await page.evaluate(() => document.body.innerText.substring(0, 4000));
        console.log('Direct search content:', content);
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
