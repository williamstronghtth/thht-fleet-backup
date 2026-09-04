const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    // Go directly to property page
    console.log('Going to property page...');
    await page.goto('https://vcpa.vcgov.org/parcel/summary/?altkey=3669363', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Click Agree if shown
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Agree') btn.click();
      }
    });
    await page.waitForTimeout(2000);
    
    console.log('On property page');
    
    // Find the Permits tab - it's in the tab navigation
    // Try clicking by text using locator
    try {
      await page.locator('text=Permits').first().click();
      console.log('Clicked Permits via locator');
    } catch (e) {
      // Fallback - look for tab links
      await page.evaluate(() => {
        const allEls = document.querySelectorAll('a, button, li, [role="tab"]');
        for (const el of allEls) {
          if (el.textContent.trim() === 'Permits') {
            el.click();
            return;
          }
        }
      });
      console.log('Clicked Permits via evaluate');
    }
    
    await page.waitForTimeout(4000);
    console.log('URL:', page.url());
    
    await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits8.png' });
    
    // Get permits content
    const content = await page.evaluate(() => document.body.innerText);
    console.log('\n=== PERMITS DATA ===\n');
    console.log(content);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
