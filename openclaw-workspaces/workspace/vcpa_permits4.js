const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    // Try direct URL with parcel ID
    console.log('Going directly to property page...');
    await page.goto('https://vcpa.vcgov.org/search/real-property/632901000430', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Click Agree if it shows
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Agree') btn.click();
      }
    });
    await page.waitForTimeout(2000);
    
    console.log('URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_prop4.png' });
    
    // Check if we're on a property page
    const pageText = await page.evaluate(() => document.body.innerText);
    
    if (pageText.includes('FALCON') || pageText.includes('Falcon')) {
      console.log('On property page!');
      
      // Look for Permits tab/link
      const allLinks = await page.$$eval('a, button, [role="tab"], li, nav a', els => 
        els.map(e => ({ text: e.textContent.trim(), href: e.href || '' }))
          .filter(e => e.text.length > 0 && e.text.length < 30)
          .slice(0, 30)
      );
      console.log('Links on page:', JSON.stringify(allLinks));
      
      // Click Permits
      const permitsClicked = await page.evaluate(() => {
        const elements = document.querySelectorAll('a, button, li, [role="tab"]');
        for (const el of elements) {
          const text = el.textContent.trim().toLowerCase();
          if (text === 'permits' || text.includes('permit')) {
            el.click();
            return 'clicked: ' + el.textContent.trim();
          }
        }
        return 'not found';
      });
      console.log('Permits:', permitsClicked);
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits4.png' });
      const content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n--- CONTENT ---\n', content);
    } else {
      console.log('Not on property page, trying search approach...');
      
      // Go to search
      await page.goto('https://vcpa.vcgov.org/search/real-property', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);
      await page.evaluate(() => {
        const btns = document.querySelectorAll('button, a');
        for (const btn of btns) {
          if (btn.textContent.trim() === 'Agree') btn.click();
        }
      });
      await page.waitForTimeout(2000);
      
      // Type parcel ID
      const input = await page.$('input[type="search"], input.form-control');
      if (input) {
        await input.type('632901000430', { delay: 50 });
        await page.waitForTimeout(3000);
        
        // Click "View Selected Parcel(s)" or first result
        await page.evaluate(() => {
          // Try clicking the AltKey link in the table
          const links = document.querySelectorAll('td a, tr a');
          for (const link of links) {
            if (link.textContent.includes('3669363') || link.href?.includes('3669363')) {
              link.click();
              return;
            }
          }
          // Or View Selected button
          const viewBtn = document.querySelector('button:contains("View Selected"), .btn-success');
          if (viewBtn) viewBtn.click();
        });
        await page.waitForTimeout(4000);
        
        console.log('After click URL:', page.url());
        const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
        console.log('Content:', content);
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
