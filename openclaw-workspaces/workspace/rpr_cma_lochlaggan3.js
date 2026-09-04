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
    console.log('On CMA page:', page.url());

    // Step 1: Click "Confirm Facts"
    console.log('\n--- Step 1: Confirm Home Facts ---');
    const confirmBtn = await page.$('text=Confirm Facts');
    if (confirmBtn) {
      await confirmBtn.click();
      await page.waitForTimeout(3000);
      console.log('Clicked Confirm Facts');
      
      // Check for any modal or expanded section
      let content = await page.evaluate(() => document.body.innerText.substring(0, 5000));
      // Look for confirm/save button in the expanded section
      const saveBtn = await page.$('button:has-text("Save"), button:has-text("Confirm"), button:has-text("OK"), button:has-text("Continue")');
      if (saveBtn) {
        const btnText = await saveBtn.textContent();
        console.log('Found button:', btnText);
        await saveBtn.click();
        await page.waitForTimeout(3000);
      }
    }

    // Step 2: Click "Find Comps"
    console.log('\n--- Step 2: Find Comps ---');
    const findCompsBtn = await page.$('text=Find Comps');
    if (findCompsBtn) {
      await findCompsBtn.click();
      await page.waitForTimeout(8000);
      console.log('Clicked Find Comps');
      console.log('URL:', page.url());
      
      // Get full page content 
      let content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n=== COMPS SEARCH PAGE ===');
      console.log(content);

      // Screenshot
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_search.png', fullPage: false });
      console.log('Screenshot saved');

      // Look for comp results - tables, lists, etc.
      const tables = await page.$$('table');
      console.log(`\nFound ${tables.length} tables`);
      
      for (let i = 0; i < tables.length; i++) {
        const tableContent = await tables[i].evaluate(t => t.innerText);
        if (tableContent.length > 50) {
          console.log(`\n--- Table ${i+1} ---`);
          console.log(tableContent.substring(0, 3000));
        }
      }

      // Look for any comp cards or listings
      const compCards = await page.$$('[class*="comp"], [class*="Comp"], [class*="result"], [class*="property"]');
      console.log(`\nComp-like elements: ${compCards.length}`);

      // Try scrolling and getting more content
      await page.evaluate(() => window.scrollTo(0, 3000));
      await page.waitForTimeout(2000);
      content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n=== AFTER SCROLL ===');
      console.log(content);

    } else {
      console.log('Find Comps button not found, trying alternative...');
      // Try clicking on step 2 directly
      const step2 = await page.$('text=Search for Comps');
      if (step2) {
        await step2.click();
        await page.waitForTimeout(5000);
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
