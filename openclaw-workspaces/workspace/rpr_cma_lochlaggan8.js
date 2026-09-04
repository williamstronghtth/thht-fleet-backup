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
    const propertyUrl = 'https://www.narrpr.com/properties/details/info/58383519?orgid=fldbaa-n&listingid=1222256&pmode=1&LocationType=Property';
    await page.goto(propertyUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(10000);
    console.log('On property page.');

    // Click CMA tab via JS
    await page.evaluate(() => {
      const els = document.querySelectorAll('a');
      for (const el of els) { if (el.textContent.trim() === 'CMA') { el.click(); break; } }
    });
    await page.waitForTimeout(8000);

    // Confirm Facts via JS
    await page.evaluate(() => {
      const btn = document.querySelector('#Valuation_ConfirmFactsBtn');
      if (btn) btn.click();
    });
    await page.waitForTimeout(3000);
    await page.evaluate(() => {
      const btn = document.querySelector('#ValuationFacts_SaveBtn');
      if (btn) btn.click();
    });
    await page.waitForTimeout(5000);
    console.log('Facts confirmed.');

    // Click Find Comps via JS
    await page.evaluate(() => {
      const els = document.querySelectorAll('a, button');
      for (const el of els) { if (el.textContent.trim() === 'Find Comps') { el.click(); break; } }
    });
    await page.waitForTimeout(10000);
    console.log('On comps search page.');

    // === EXAMINE THE FILTER UI ===
    // Get detailed info about the status filter elements
    const statusInfo = await page.evaluate(() => {
      const results = [];
      // Look for checkboxes
      const checkboxes = document.querySelectorAll('input[type="checkbox"]');
      for (const cb of checkboxes) {
        const label = cb.closest('label') || cb.parentElement;
        results.push({
          type: 'checkbox',
          id: cb.id,
          name: cb.name,
          value: cb.value,
          checked: cb.checked,
          label: label ? label.textContent.trim().substring(0, 50) : '',
          class: cb.className.substring(0, 50)
        });
      }
      // Also look for filter list items
      const filterItems = document.querySelectorAll('[class*="filter"] li, [class*="status"] li, [class*="Filter"] li, [class*="Status"] li');
      for (const item of filterItems) {
        results.push({
          type: 'filterItem',
          text: item.textContent.trim().substring(0, 50),
          class: item.className.substring(0, 80),
          hasInput: item.querySelector('input') ? true : false
        });
      }
      return results;
    });
    console.log('\n=== STATUS FILTER ELEMENTS ===');
    console.log(JSON.stringify(statusInfo, null, 2));

    // Get the full HTML of the status section
    const statusHtml = await page.evaluate(() => {
      // Find the section containing "PROPERTY STATUS"
      const allEls = document.querySelectorAll('*');
      for (const el of allEls) {
        if (el.textContent.includes('PROPERTY STATUS') && el.children.length < 20 && el.innerHTML.length < 5000) {
          return el.innerHTML.substring(0, 3000);
        }
      }
      return 'Not found';
    });
    console.log('\n=== STATUS SECTION HTML ===');
    console.log(statusHtml);

    // Also find the OFF MARKET DATE section
    const dateHtml = await page.evaluate(() => {
      const allEls = document.querySelectorAll('*');
      for (const el of allEls) {
        if (el.textContent.includes('OFF MARKET DATE') && el.children.length < 15 && el.innerHTML.length < 3000) {
          return el.innerHTML.substring(0, 2000);
        }
      }
      return 'Not found';
    });
    console.log('\n=== DATE SECTION HTML ===');
    console.log(dateHtml);

    // Get the geography section
    const geoHtml = await page.evaluate(() => {
      const allEls = document.querySelectorAll('*');
      for (const el of allEls) {
        if (el.textContent.includes('Within this Zip') && el.children.length < 15 && el.innerHTML.length < 3000) {
          return el.innerHTML.substring(0, 2000);
        }
      }
      return 'Not found';
    });
    console.log('\n=== GEOGRAPHY SECTION HTML ===');
    console.log(geoHtml);

    // Find the Search button
    const searchBtnInfo = await page.evaluate(() => {
      const els = document.querySelectorAll('a, button, input[type="submit"]');
      const results = [];
      for (const el of els) {
        if (el.textContent.trim() === 'Search' && el.offsetWidth > 0) {
          results.push({
            tag: el.tagName,
            id: el.id,
            class: el.className.toString().substring(0, 80),
            href: el.href || '',
            onclick: el.getAttribute('onclick') || ''
          });
        }
      }
      return results;
    });
    console.log('\n=== SEARCH BUTTON ===');
    console.log(JSON.stringify(searchBtnInfo, null, 2));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
