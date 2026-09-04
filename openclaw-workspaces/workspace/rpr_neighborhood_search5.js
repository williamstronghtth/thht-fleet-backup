const { chromium } = require('playwright');

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

    // Try RPR's Neighborhood Search directly
    await page.goto('https://www.narrpr.com/neighborhoods', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log('Neighborhood search URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_nbh_search.png' });
    
    let content = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('Page:', content);

    // Look for a search input
    const inputs = await page.$$eval('input:visible', els => els.map(e => ({
      type: e.type, placeholder: e.placeholder, id: e.id, name: e.name, className: e.className
    })));
    console.log('Inputs:', JSON.stringify(inputs));

    // Try typing in any search input
    const searchInput = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type('Waters Edge Port Orange', { delay: 80 });
      await page.waitForTimeout(4000);
      
      // Check suggestions
      const allText = await page.evaluate(() => document.body.innerText.substring(0, 5000));
      console.log('\nAfter typing:', allText);
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_nbh_suggestions.png' });
    }

    // Also try the map search approach with the search term
    console.log('\n\n--- Trying Map Search Approach ---');
    await page.goto('https://www.narrpr.com/properties/search?q=Waters+Edge+Port+Orange+FL&searchType=neighborhood', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('Map search URL:', page.url());
    content = await page.evaluate(() => document.body.innerText.substring(0, 5000));
    console.log('Content:', content);
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_map_search.png' });

    // Try one more thing: go to property search and switch to Public Records first, then search
    console.log('\n\n--- Trying Property Search with Public Records ---');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    // First switch to "Public Records" search type before typing
    // Look for tabs or toggles near the search bar
    const allLinks = await page.$$eval('a:visible, button:visible', els => 
      els.filter(e => e.textContent.trim().length < 30 && e.textContent.trim().length > 0)
        .map(e => ({ text: e.textContent.trim(), tag: e.tagName, href: e.href || '', class: e.className.substring(0, 50) }))
        .slice(0, 30)
    );
    console.log('Visible links/buttons:', JSON.stringify(allLinks, null, 2));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
