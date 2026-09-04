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
    console.log('Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in.');

    // Go to CMA page
    const cmaUrl = 'https://www.narrpr.com/homes/fl/new-smyrna-beach/32168/1108-loch-laggan-ct/58383519-valuation.aspx?orgid=fldbaa-n&listingid=1222256&pmode=1';
    await page.goto(cmaUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);

    // Step 1: Confirm Facts
    await page.click('text=Confirm Facts');
    await page.waitForTimeout(3000);
    await page.click('.ui-dialog >> text=Confirm Facts and Close');
    await page.waitForTimeout(5000);
    console.log('Facts confirmed.');

    // Step 2: Find Comps
    await page.click('text=Find Comps');
    await page.waitForTimeout(8000);
    console.log('On comps search page.');

    // Select "Closed" status
    console.log('\nSetting filters...');
    
    // Click on Property Status - select Closed
    // First let's find the status checkboxes/options
    const statusSection = await page.evaluate(() => {
      const labels = document.querySelectorAll('label, span, div');
      const results = [];
      for (const el of labels) {
        const text = el.textContent.trim();
        if (text === 'Closed' || text === 'Active For Sale' || text === 'Pending') {
          results.push({ text, tag: el.tagName, class: el.className.substring(0, 50), id: el.id });
        }
      }
      return results;
    });
    console.log('Status elements:', JSON.stringify(statusSection));

    // Click "Closed" to select it
    try {
      await page.click('text=Closed', { timeout: 5000 });
      console.log('Selected Closed');
      await page.waitForTimeout(1000);
    } catch(e) {
      console.log('Could not click Closed directly');
    }

    // Set date range - last 12 months
    try {
      await page.click('text=Within last 12 months', { timeout: 5000 });
      console.log('Set Within last 12 months');
    } catch(e) {
      console.log('Could not set date range directly, trying dropdown...');
      // Try selecting from dropdown
      const dateSelect = await page.$('select:near(:text("OFF MARKET DATE"))');
      if (dateSelect) {
        await dateSelect.selectOption({ label: 'Within last 12 months' });
        console.log('Selected 12 months from dropdown');
      }
    }

    // Set geography - Within this Zip
    try {
      await page.click('text=Within this Zip', { timeout: 5000 });
      console.log('Selected Within this Zip');
      await page.waitForTimeout(2000);
    } catch(e) {
      console.log('Could not select zip geography');
    }

    // Take screenshot of filters
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_filters.png', fullPage: false });

    // Click Search
    console.log('\nSearching for comps...');
    try {
      // Find the search button in the comps interface
      const searchBtn = await page.$('a:has-text("Search"):not(:has-text("Search for")):not(:has-text("Search an")), button:has-text("Search"):not(:has-text("Search for")):not(:has-text("Search an"))');
      if (searchBtn) {
        await searchBtn.click();
        console.log('Clicked Search button');
      } else {
        // Try finding by exact text
        await page.click('a:text-is("Search"), button:text-is("Search")', { timeout: 5000 });
        console.log('Clicked Search (exact match)');
      }
      
      await page.waitForTimeout(10000);
      console.log('Search complete. URL:', page.url());

      // Get results
      let content = await page.evaluate(() => document.body.innerText.substring(0, 20000));
      console.log('\n=== SEARCH RESULTS ===');
      console.log(content);

      // Screenshot results
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_results.png', fullPage: false });

      // Scroll down to see more results
      await page.evaluate(() => window.scrollTo(0, 5000));
      await page.waitForTimeout(2000);
      content = await page.evaluate(() => document.body.innerText.substring(0, 20000));
      console.log('\n=== AFTER SCROLL ===');
      console.log(content);

    } catch(e) {
      console.log('Search failed:', e.message.substring(0, 200));
      
      // List all visible buttons/links
      const allBtns = await page.evaluate(() => {
        const els = document.querySelectorAll('a, button');
        return Array.from(els)
          .filter(e => e.offsetWidth > 0 && e.offsetHeight > 0)
          .map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 40), class: e.className.toString().substring(0, 50) }));
      });
      console.log('All visible buttons:', JSON.stringify(allBtns, null, 2));
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
