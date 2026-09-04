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
    await input.type('785 Falcon', { delay: 80 });
    await page.waitForTimeout(4000);
    console.log('Searched');
    
    // Try clicking on AltKey "3669363" which should be a link
    const linkClicked = await page.evaluate(() => {
      const links = document.querySelectorAll('a');
      for (const link of links) {
        if (link.textContent.includes('3669363')) {
          console.log('Found link:', link.href);
          link.click();
          return link.href;
        }
      }
      // Try clicking any link in the table that contains the parcel
      const tds = document.querySelectorAll('td');
      for (const td of tds) {
        if (td.textContent.includes('3669363')) {
          const link = td.querySelector('a');
          if (link) {
            link.click();
            return 'clicked td link';
          }
          td.click();
          return 'clicked td';
        }
      }
      return 'not found';
    });
    console.log('Link clicked:', linkClicked);
    await page.waitForTimeout(5000);
    
    console.log('URL after click:', page.url());
    
    // If URL changed, we're on property page
    if (page.url().includes('3669363') || page.url().includes('parcel')) {
      console.log('On property page!');
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_prop6.png' });
      
      // Click Permits
      await page.evaluate(() => {
        const els = document.querySelectorAll('a, button, li, span, div');
        for (const el of els) {
          if (el.textContent.trim().toLowerCase() === 'permits') {
            el.click();
            return;
          }
        }
      });
      await page.waitForTimeout(4000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits6.png' });
      const content = await page.evaluate(() => document.body.innerText);
      console.log('\n--- CONTENT ---\n', content.substring(0, 15000));
    } else {
      console.log('Still on search page, checking page structure...');
      
      // Get all clickable elements in the results
      const clickables = await page.$$eval('table a, table button, table td[onclick]', els => 
        els.map(e => ({ tag: e.tagName, text: e.textContent.trim().substring(0, 50), href: e.href || '', onclick: e.onclick ? 'yes' : 'no' }))
      );
      console.log('Clickable elements in table:', JSON.stringify(clickables, null, 2));
      
      // Also try double-clicking the row
      await page.evaluate(() => {
        const rows = document.querySelectorAll('tbody tr');
        for (const row of rows) {
          if (row.textContent.includes('FALCON')) {
            row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
            return;
          }
        }
      });
      await page.waitForTimeout(3000);
      console.log('URL after dblclick:', page.url());
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
