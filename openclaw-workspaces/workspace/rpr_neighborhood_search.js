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
    console.log('Logged in. URL:', page.url());

    // Go to home/search page
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    // Find the search input
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type(NEIGHBORHOOD, { delay: 80 });
      console.log('Typed:', NEIGHBORHOOD);
      await page.waitForTimeout(4000);

      // Screenshot to see suggestions
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_neighborhood_suggestions.png' });
      console.log('Screenshot saved (suggestions)');

      // Look for autocomplete/suggestions
      const suggestions = await page.$$eval(
        '[class*="suggestion"], [class*="autocomplete"] li, [class*="dropdown"] li, [role="option"], [role="listbox"] [role="option"], [class*="result"] li, [class*="list-item"]',
        els => els.map(e => ({ text: e.textContent.trim(), classes: e.className })).slice(0, 10)
      );
      console.log('Suggestions found:', JSON.stringify(suggestions, null, 2));

      // Try to find a neighborhood-specific suggestion
      let clicked = false;
      for (const sel of ['[role="option"]', '[class*="suggestion"]', '[class*="autocomplete"] li', '[class*="dropdown"] li']) {
        const items = await page.$$(sel);
        for (const item of items) {
          const text = await item.textContent();
          if (text.toLowerCase().includes('waters edge') || text.toLowerCase().includes('neighborhood')) {
            await item.click();
            console.log('Clicked suggestion:', text.trim());
            clicked = true;
            break;
          }
        }
        if (clicked) break;
      }

      if (!clicked) {
        // Just press Enter
        await page.keyboard.press('Enter');
        console.log('Pressed Enter');
      }

      await page.waitForTimeout(6000);
      console.log('Result URL:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_neighborhood_results.png' });
      console.log('Screenshot saved (results)');

      // Get page text
      const content = await page.evaluate(() => document.body.innerText.substring(0, 6000));
      console.log('\n--- PAGE CONTENT ---\n', content);

    } else {
      console.log('No search input found');
      // List all inputs for debugging
      const inputs = await page.$$eval('input:visible', els => els.map(e => ({ type: e.type, placeholder: e.placeholder, id: e.id, name: e.name })));
      console.log('Visible inputs:', JSON.stringify(inputs));
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
