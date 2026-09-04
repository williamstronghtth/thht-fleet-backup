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

    // Go to property page
    await page.goto('https://www.narrpr.com/properties/details/info/58383519?orgid=fldbaa-n&listingid=1222256&pmode=1&LocationType=Property', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(10000);

    // Click CMA tab via JS
    await page.evaluate(() => {
      const els = document.querySelectorAll('a');
      for (const el of els) { if (el.textContent.trim() === 'CMA') { el.click(); break; } }
    });
    await page.waitForTimeout(8000);

    // Confirm Facts
    await page.evaluate(() => document.querySelector('#Valuation_ConfirmFactsBtn')?.click());
    await page.waitForTimeout(3000);
    await page.evaluate(() => document.querySelector('#ValuationFacts_SaveBtn')?.click());
    await page.waitForTimeout(5000);
    console.log('Facts confirmed.');

    // Click Find Comps
    await page.evaluate(() => {
      const els = document.querySelectorAll('a, button');
      for (const el of els) { if (el.textContent.trim() === 'Find Comps') { el.click(); break; } }
    });
    await page.waitForTimeout(10000);
    console.log('On comps search page.');

    // === SET FILTERS ===
    
    // 1. Uncheck Active For Sale (#ctl19), Pending (#ctl20), Active Under Contract (#ctl21)
    // Keep Closed (#ctl22) checked
    console.log('Setting status filters...');
    await page.evaluate(() => {
      const ctl19 = document.querySelector('#ctl19'); // Active For Sale
      const ctl20 = document.querySelector('#ctl20'); // Pending
      const ctl21 = document.querySelector('#ctl21'); // Active Under Contract
      const ctl22 = document.querySelector('#ctl22'); // Closed
      
      // Uncheck active statuses
      if (ctl19 && ctl19.checked) { ctl19.click(); }
      if (ctl20 && ctl20.checked) { ctl20.click(); }
      if (ctl21 && ctl21.checked) { ctl21.click(); }
      // Make sure Closed is checked
      if (ctl22 && !ctl22.checked) { ctl22.click(); }
    });
    await page.waitForTimeout(2000);

    // Verify filter state
    const filterState = await page.evaluate(() => ({
      activeForSale: document.querySelector('#ctl19')?.checked,
      pending: document.querySelector('#ctl20')?.checked,
      activeUnder: document.querySelector('#ctl21')?.checked,
      closed: document.querySelector('#ctl22')?.checked
    }));
    console.log('Filter state:', JSON.stringify(filterState));

    // 2. Set date range to "Within last 12 months" (value=360)
    console.log('Setting date range to 12 months...');
    await page.evaluate(() => {
      const sel = document.querySelector('select[name="RprField_41"]');
      if (sel) {
        sel.value = '360';
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    await page.waitForTimeout(1000);

    // 3. Set geography to "Within this Zip" (value=6)
    console.log('Setting geography to Within this Zip...');
    await page.evaluate(() => {
      const sel = document.querySelector('select.tbPropertyGeo');
      if (sel) {
        sel.value = '6';
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    await page.waitForTimeout(3000);

    // 4. Click Search button (#VCSD_SearchBtn)
    console.log('Searching...');
    await page.evaluate(() => {
      document.querySelector('#VCSD_SearchBtn')?.click();
    });
    await page.waitForTimeout(15000);
    console.log('Search complete!');

    // Get results
    const content = await page.evaluate(() => document.body.innerText.substring(0, 25000));
    console.log('\n=== SEARCH RESULTS ===');
    console.log(content);

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_final.png', fullPage: false });

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
