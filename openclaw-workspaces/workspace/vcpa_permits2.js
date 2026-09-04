const { chromium } = require('playwright');

const ADDRESS = '785 Falcon Dr';

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
    const agreeBtn = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Agree') {
          btn.click();
          return 'clicked';
        }
      }
      return 'not found';
    });
    console.log('Agree button:', agreeBtn);
    await page.waitForTimeout(2000);
    
    // Now search for the address
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.type(ADDRESS, { delay: 80 });
      console.log('Typed:', ADDRESS);
      await page.waitForTimeout(4000);
      
      // Look for results/suggestions
      const pageText = await page.evaluate(() => document.body.innerText);
      
      // Check if we see "785 Falcon" in results
      if (pageText.includes('785 FALCON') || pageText.includes('785 Falcon')) {
        console.log('Found address in results!');
      }
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_search2.png' });
      
      // Try to click on the matching result
      const clicked = await page.evaluate(() => {
        const elements = document.querySelectorAll('a, tr, div, li');
        for (const el of elements) {
          if (el.textContent.includes('785 FALCON') || el.textContent.includes('785 Falcon')) {
            el.click();
            return el.textContent.substring(0, 100);
          }
        }
        return 'not found';
      });
      console.log('Clicked result:', clicked);
      await page.waitForTimeout(4000);
      
      console.log('URL:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_property.png' });
      
      // Now look for "Permits" tab/link
      const permitsClicked = await page.evaluate(() => {
        const links = document.querySelectorAll('a, button, [role="tab"]');
        for (const link of links) {
          if (link.textContent.toLowerCase().includes('permit')) {
            link.click();
            return 'clicked permits';
          }
        }
        return 'permits not found';
      });
      console.log('Permits:', permitsClicked);
      await page.waitForTimeout(4000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_permits.png' });
      
      // Get permit data
      const content = await page.evaluate(() => document.body.innerText.substring(0, 10000));
      console.log('\n--- PERMIT DATA ---\n', content);

    } else {
      console.log('Search input not found');
      const content = await page.evaluate(() => document.body.innerText.substring(0, 3000));
      console.log('Page content:', content);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
