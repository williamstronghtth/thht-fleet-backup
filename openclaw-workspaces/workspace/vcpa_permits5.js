const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('Going to search page...');
    await page.goto('https://vcpa.vcgov.org/search/real-property', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Click Agree
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Agree') btn.click();
      }
    });
    await page.waitForTimeout(2000);
    
    // Search for address
    const input = await page.$('input[type="search"], input.form-control');
    if (input) {
      await input.type('785 Falcon', { delay: 80 });
      await page.waitForTimeout(4000);
      console.log('Searched for 785 Falcon');
      
      // Click the checkbox on the first result row
      await page.evaluate(() => {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        for (const cb of checkboxes) {
          const row = cb.closest('tr');
          if (row && row.textContent.includes('FALCON')) {
            cb.click();
            return;
          }
        }
        // Or just click first checkbox in table body
        const firstCb = document.querySelector('tbody input[type="checkbox"]');
        if (firstCb) firstCb.click();
      });
      console.log('Selected checkbox');
      await page.waitForTimeout(1000);
      
      // Click "View Selected Parcel(s)" button
      await page.evaluate(() => {
        const btns = document.querySelectorAll('button, a');
        for (const btn of btns) {
          if (btn.textContent.includes('View Selected')) {
            btn.click();
            return;
          }
        }
      });
      console.log('Clicked View Selected');
      await page.waitForTimeout(5000);
      
      console.log('URL:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_property5.png' });
      
      // Now look for Permits tab
      const tabs = await page.$$eval('a, button, li, [role="tab"], nav a', els => 
        els.map(e => e.textContent.trim()).filter(t => t.length > 0 && t.length < 30)
      );
      console.log('Available tabs/links:', tabs.filter(t => t.toLowerCase().includes('permit') || t.toLowerCase().includes('sales') || t.toLowerCase().includes('value')));
      
      // Click Permits
      await page.evaluate(() => {
        const elements = document.querySelectorAll('a, button, li, span');
        for (const el of elements) {
          if (el.textContent.trim().toLowerCase() === 'permits') {
            el.click();
            return;
          }
        }
      });
      console.log('Clicked Permits tab');
      await page.waitForTimeout(4000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits5.png' });
      
      const content = await page.evaluate(() => document.body.innerText);
      
      // Extract permit info - look for roof, HVAC, water heater related permits
      const lines = content.split('\n');
      const permitLines = lines.filter(l => 
        l.toLowerCase().includes('roof') || 
        l.toLowerCase().includes('hvac') || 
        l.toLowerCase().includes('a/c') ||
        l.toLowerCase().includes('air condition') ||
        l.toLowerCase().includes('water heater') ||
        l.toLowerCase().includes('permit') ||
        l.toLowerCase().includes('mechanical') ||
        l.toLowerCase().includes('electrical') ||
        l.match(/\d{4}/) // years
      );
      
      console.log('\n--- PERMIT INFO ---');
      console.log(content.substring(0, 12000));
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
