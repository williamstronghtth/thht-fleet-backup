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
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type(NEIGHBORHOOD, { delay: 80 });
      await page.waitForTimeout(4000);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(6000);
      console.log('On search results:', page.url());

      // Now change to Public Records view and clear filters
      // First, click "Public Records" tab/toggle to see all properties
      const publicRecordsBtn = await page.$('text=Public Records');
      if (publicRecordsBtn) {
        await publicRecordsBtn.click();
        console.log('Clicked Public Records');
        await page.waitForTimeout(3000);
      }

      // Clear property type filter - click on "Property Type" then select all or clear
      const propTypeBtn = await page.$('text=Property Type');
      if (propTypeBtn) {
        await propTypeBtn.click();
        console.log('Clicked Property Type filter');
        await page.waitForTimeout(2000);
        await page.screenshot({ path: '/root/.openclaw/workspace/rpr_proptype_dropdown.png' });
        
        // Look for checkboxes or "Select All" or individual options
        const filterContent = await page.evaluate(() => {
          const dropdowns = document.querySelectorAll('[class*="dropdown"], [class*="filter"], [class*="popover"], [class*="menu"]');
          return Array.from(dropdowns).map(d => d.innerText.substring(0, 500)).join('\n---\n');
        });
        console.log('Filter dropdowns:', filterContent);

        // Try to find and click "Single Family" or "Residential" specifically
        const checkboxes = await page.$$('input[type="checkbox"]');
        console.log('Found', checkboxes.length, 'checkboxes');
        
        for (const cb of checkboxes) {
          const label = await cb.evaluate(e => {
            const lbl = e.closest('label') || e.parentElement;
            return lbl ? lbl.textContent.trim() : '';
          });
          const checked = await cb.isChecked();
          console.log(`  Checkbox: "${label}" checked=${checked}`);
        }
      }

      // Try clicking "Type/Status" dropdown  
      const typeStatusBtn = await page.$('text=Type/Status');
      if (typeStatusBtn) {
        await typeStatusBtn.click();
        console.log('Clicked Type/Status');
        await page.waitForTimeout(2000);
        await page.screenshot({ path: '/root/.openclaw/workspace/rpr_typestatus.png' });
        
        const dropdownText = await page.evaluate(() => document.body.innerText.substring(0, 4000));
        console.log('Page content:', dropdownText);
      }

      // Try to see all filters and reset them
      // Look for a "Reset" or "Clear" button
      const resetBtn = await page.$('text=Reset, text=Clear All, text=Clear Filters, button:has-text("Reset")');
      if (resetBtn) {
        await resetBtn.click();
        console.log('Clicked reset');
        await page.waitForTimeout(3000);
      }

      // Final screenshot and content
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_neighborhood_final.png' });
      const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
      console.log('\n--- FINAL PAGE ---\n', content);

    }
  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
