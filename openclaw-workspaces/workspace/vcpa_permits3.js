const { chromium } = require('playwright');

const ADDRESS = '785 Falcon';

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('Going to Volusia County Property Appraiser...');
    await page.goto('https://vcpa.vcgov.org/search/real-property', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Click "Agree" button on disclaimer
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Agree') {
          btn.click();
          return;
        }
      }
    });
    console.log('Clicked Agree');
    await page.waitForTimeout(2000);
    
    // Find the main search input in the table area (not header)
    // Look for input with placeholder about "Name", "Address", etc
    const mainInput = await page.$('input[type="search"], input.form-control, input[placeholder*="Name"], input[placeholder*="Address"]');
    
    if (mainInput) {
      await mainInput.click();
      await mainInput.type(ADDRESS, { delay: 100 });
      console.log('Typed in main input:', ADDRESS);
    } else {
      // Try the header search
      const headerInput = await page.$('input[type="text"]:visible');
      if (headerInput) {
        await headerInput.click();
        await headerInput.fill('');
        await headerInput.type(ADDRESS, { delay: 100 });
        console.log('Typed in header input:', ADDRESS);
        
        // Click the search button (blue magnifying glass)
        const searchBtn = await page.$('button[type="submit"], button.btn-primary, [class*="search-btn"], [aria-label*="search"]');
        if (searchBtn) {
          await searchBtn.click();
          console.log('Clicked search button');
        } else {
          await page.keyboard.press('Enter');
          console.log('Pressed Enter');
        }
      }
    }
    
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_results3.png' });
    
    // Check for results
    const resultsText = await page.evaluate(() => document.body.innerText);
    
    if (resultsText.includes('FALCON') || resultsText.includes('Falcon')) {
      console.log('Found Falcon in results!');
      
      // Click on the row containing Falcon
      await page.evaluate(() => {
        const rows = document.querySelectorAll('tr');
        for (const row of rows) {
          if (row.textContent.toUpperCase().includes('FALCON')) {
            const link = row.querySelector('a');
            if (link) link.click();
            else row.click();
            return;
          }
        }
      });
      await page.waitForTimeout(4000);
      console.log('URL after click:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_property3.png' });
      
      // Look for Permits tab
      const clickedPermits = await page.evaluate(() => {
        const elements = document.querySelectorAll('a, button, [role="tab"], li');
        for (const el of elements) {
          if (el.textContent.toLowerCase().includes('permit')) {
            el.click();
            return 'clicked: ' + el.textContent.trim();
          }
        }
        return 'not found';
      });
      console.log('Permits tab:', clickedPermits);
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits3.png' });
      const permitContent = await page.evaluate(() => document.body.innerText.substring(0, 12000));
      console.log('\n--- PERMIT DATA ---\n', permitContent);
    } else {
      console.log('Falcon not found in results');
      console.log('Page text sample:', resultsText.substring(0, 2000));
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
