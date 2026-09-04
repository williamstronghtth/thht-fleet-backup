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
    
    // Find search input and type address
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible, input[placeholder*="Search"]:visible, input[placeholder*="search"]:visible, input[placeholder*="Address"]:visible');
    
    if (!searchInput) {
      // List all inputs to find the right one
      const inputs = await page.$$eval('input:visible', els => els.map(e => ({
        type: e.type, placeholder: e.placeholder, id: e.id, name: e.name, class: e.className.substring(0, 50)
      })));
      console.log('Visible inputs:', JSON.stringify(inputs, null, 2));
    }
    
    // Try to find and use the search
    const allInputs = await page.$$('input:visible');
    console.log('Found', allInputs.length, 'visible inputs');
    
    for (const input of allInputs) {
      const placeholder = await input.getAttribute('placeholder');
      const type = await input.getAttribute('type');
      console.log('Input:', type, placeholder);
    }
    
    // Type in first text input
    const textInput = await page.$('input[type="text"]:visible');
    if (textInput) {
      await textInput.click();
      await textInput.type(ADDRESS, { delay: 80 });
      console.log('Typed:', ADDRESS);
      await page.waitForTimeout(3000);
      
      // Screenshot to see suggestions
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_search.png' });
      
      // Look for autocomplete suggestions
      const suggestions = await page.evaluate(() => {
        const items = document.querySelectorAll('[class*="suggestion"], [class*="autocomplete"], [class*="dropdown"] li, [class*="result"], [role="option"], [class*="list-item"], [class*="search-result"]');
        return Array.from(items).map(e => e.textContent.trim()).slice(0, 10);
      });
      console.log('Suggestions:', suggestions);
      
      // Get page content
      const content = await page.evaluate(() => document.body.innerText.substring(0, 5000));
      console.log('\n--- PAGE CONTENT ---\n', content);
      
      // Try pressing Enter or clicking a result
      await page.keyboard.press('Enter');
      await page.waitForTimeout(4000);
      
      console.log('URL after search:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/vcpa_results.png' });
      
      const resultsContent = await page.evaluate(() => document.body.innerText.substring(0, 8000));
      console.log('\n--- RESULTS ---\n', resultsContent);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
