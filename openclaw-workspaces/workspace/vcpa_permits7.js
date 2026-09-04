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
    
    // Search
    const input = await page.$('input[type="search"], input.form-control');
    await input.type('785 Falcon', { delay: 80 });
    await page.waitForTimeout(4000);
    
    // Double-click on first FALCON row
    await page.evaluate(() => {
      const rows = document.querySelectorAll('tbody tr');
      for (const row of rows) {
        if (row.textContent.includes('FALCON')) {
          row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
          return;
        }
      }
    });
    await page.waitForTimeout(5000);
    
    console.log('Property URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_prop7.png' });
    
    // Look for and click Permits tab
    const tabs = await page.$$eval('a, li, button, [role="tab"]', els => 
      els.map(e => e.textContent.trim()).filter(t => t.length > 0 && t.length < 25)
    );
    console.log('Available tabs:', tabs.slice(0, 30));
    
    await page.evaluate(() => {
      const els = document.querySelectorAll('a, li, button, span');
      for (const el of els) {
        const text = el.textContent.trim().toLowerCase();
        if (text === 'permits' || text === 'permit') {
          el.click();
          return;
        }
      }
    });
    console.log('Clicked Permits');
    await page.waitForTimeout(4000);
    
    await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits7.png' });
    
    // Get permit content
    const content = await page.evaluate(() => document.body.innerText);
    console.log('\n=== PERMITS DATA ===\n');
    console.log(content.substring(0, 15000));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
