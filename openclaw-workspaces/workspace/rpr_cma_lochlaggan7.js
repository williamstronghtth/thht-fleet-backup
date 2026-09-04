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

    // Go directly to the property page first (not the CMA page)
    const propertyUrl = 'https://www.narrpr.com/properties/details/info/58383519?orgid=fldbaa-n&listingid=1222256&pmode=1&LocationType=Property';
    console.log('Going to property page...');
    await page.goto(propertyUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(10000);
    console.log('Property page loaded:', page.url());

    // Now click on the CMA tab
    console.log('\nClicking CMA tab...');
    try {
      await page.click('text=CMA', { timeout: 10000 });
      await page.waitForTimeout(8000);
      console.log('CMA tab clicked, URL:', page.url());
    } catch(e) {
      console.log('CMA tab click failed, trying JS...');
      await page.evaluate(() => {
        const els = document.querySelectorAll('a');
        for (const el of els) {
          if (el.textContent.trim() === 'CMA') {
            el.click();
            return;
          }
        }
      });
      await page.waitForTimeout(8000);
    }

    // Take screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_cma_tab.png', fullPage: false });

    // Check for Confirm Facts button visibility
    const confirmVisible = await page.evaluate(() => {
      const el = document.querySelector('#Valuation_ConfirmFactsBtn');
      if (!el) return 'not found';
      return { visible: el.offsetWidth > 0 && el.offsetHeight > 0, display: window.getComputedStyle(el).display, text: el.textContent };
    });
    console.log('Confirm Facts button:', JSON.stringify(confirmVisible));

    // Now try clicking Confirm Facts using JS click (bypass visibility)
    console.log('\nClicking Confirm Facts via JS...');
    await page.evaluate(() => {
      const btn = document.querySelector('#Valuation_ConfirmFactsBtn');
      if (btn) btn.click();
    });
    await page.waitForTimeout(5000);

    // Check for dialog
    const dialogOpen = await page.evaluate(() => {
      const dialog = document.querySelector('.ui-dialog');
      return dialog ? dialog.innerText.substring(0, 500) : 'No dialog';
    });
    console.log('Dialog:', dialogOpen);

    if (dialogOpen !== 'No dialog') {
      // Click Confirm Facts and Close
      console.log('Clicking Confirm Facts and Close...');
      await page.evaluate(() => {
        const btn = document.querySelector('#ValuationFacts_SaveBtn');
        if (btn) btn.click();
      });
      await page.waitForTimeout(5000);
    }

    // Now click Find Comps
    console.log('\nClicking Find Comps...');
    await page.evaluate(() => {
      const els = document.querySelectorAll('a, button');
      for (const el of els) {
        if (el.textContent.trim() === 'Find Comps') {
          el.click();
          return;
        }
      }
    });
    await page.waitForTimeout(10000);
    console.log('URL after Find Comps:', page.url());

    // Get page content
    let content = await page.evaluate(() => document.body.innerText.substring(0, 5000));
    console.log('\n=== COMPS SEARCH PAGE ===');
    console.log(content);

    // Now set filters and search
    // Select Closed status
    console.log('\n--- Setting Closed status ---');
    await page.evaluate(() => {
      // Find checkboxes or clickable items for status
      const labels = document.querySelectorAll('label, li, a, span');
      for (const el of labels) {
        const t = el.textContent.trim();
        if (t === 'Closed') {
          el.click();
          break;
        }
      }
    });
    await page.waitForTimeout(2000);

    // Select "Within last 12 months" from off market date
    console.log('Setting date range...');
    await page.evaluate(() => {
      const selects = document.querySelectorAll('select');
      for (const sel of selects) {
        for (const opt of sel.options) {
          if (opt.text.includes('12 months')) {
            sel.value = opt.value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            break;
          }
        }
      }
    });
    await page.waitForTimeout(1000);

    // Select "Within this Zip"
    console.log('Setting geography: Within this Zip...');
    await page.evaluate(() => {
      const els = document.querySelectorAll('a, li, label, span');
      for (const el of els) {
        if (el.textContent.trim() === 'Within this Zip') {
          el.click();
          break;
        }
      }
    });
    await page.waitForTimeout(3000);

    // Screenshot before search
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_before_search.png', fullPage: false });

    // Click Search
    console.log('Clicking Search...');
    await page.evaluate(() => {
      // Find the search button (not "Search for" or "Search an area")
      const els = document.querySelectorAll('a, button');
      for (const el of els) {
        const t = el.textContent.trim();
        if (t === 'Search' && el.offsetWidth > 0) {
          el.click();
          return true;
        }
      }
      return false;
    });
    await page.waitForTimeout(15000);

    // Get results
    content = await page.evaluate(() => document.body.innerText.substring(0, 20000));
    console.log('\n=== SEARCH RESULTS ===');
    console.log(content);

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_results.png', fullPage: false });

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
