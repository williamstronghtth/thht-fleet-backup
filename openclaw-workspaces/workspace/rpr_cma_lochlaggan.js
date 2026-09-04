const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Login
    console.log('Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in. URL:', page.url());

    // Search for the property
    const addr = '1108 Loch Laggan Ct, New Smyrna Beach, FL 32168';
    console.log('\nSearching for:', addr);
    
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    // Find search input
    const topSearch = await page.$('input[type="text"]:visible, input[type="search"]:visible');
    if (topSearch) {
      await topSearch.click();
      await topSearch.fill('');
      await topSearch.type(addr, { delay: 50 });
      await page.waitForTimeout(3000);
      
      // Click first suggestion
      const firstSuggestion = await page.$('[role="option"]:first-child, [class*="suggestion"]:first-child, [class*="autocomplete"] li:first-child');
      if (firstSuggestion) {
        await firstSuggestion.click();
        console.log('Clicked suggestion');
      } else {
        await page.keyboard.press('Enter');
      }
      await page.waitForTimeout(8000);
      console.log('Property page URL:', page.url());
    }

    // Get property page content - look for valuation data
    let content = await page.evaluate(() => document.body.innerText.substring(0, 6000));
    console.log('\n=== PROPERTY PAGE ===');
    console.log(content);

    // Try to find and click CMA/Comps link
    console.log('\n=== Looking for CMA/Comps links ===');
    const links = await page.$$eval('a, button', els => 
      els.filter(e => {
        const text = e.textContent.toLowerCase();
        return text.includes('cma') || text.includes('comp') || text.includes('comparable') || text.includes('valuation');
      }).map(e => ({ text: e.textContent.trim().substring(0, 80), href: e.href || '', tag: e.tagName }))
    );
    console.log('Found links:', JSON.stringify(links, null, 2));

    // Try clicking on "Comps" or similar
    for (const linkText of ['Comps', 'CMA', 'Comparable', 'Valuation']) {
      const link = await page.$(`a:has-text("${linkText}"), button:has-text("${linkText}")`);
      if (link) {
        console.log(`\nClicking "${linkText}" link...`);
        await link.click();
        await page.waitForTimeout(5000);
        console.log('URL after click:', page.url());
        content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
        console.log('\n=== COMPS/CMA PAGE ===');
        console.log(content);
        break;
      }
    }

    // Also check for nearby sales / sold properties section on the page
    console.log('\n=== Looking for sold/nearby data ===');
    const soldLinks = await page.$$eval('a, button, [class*="tab"], [role="tab"]', els => 
      els.filter(e => {
        const text = e.textContent.toLowerCase();
        return text.includes('sold') || text.includes('sale') || text.includes('history') || text.includes('nearby') || text.includes('market');
      }).map(e => ({ text: e.textContent.trim().substring(0, 80), href: e.href || '', tag: e.tagName }))
    );
    console.log('Sold/nearby links:', JSON.stringify(soldLinks, null, 2));

    // Try to navigate to RVM/valuation details
    const rprPropertyUrl = page.url();
    if (rprPropertyUrl.includes('narrpr.com')) {
      // Try comps URL pattern
      const compsUrl = rprPropertyUrl.replace(/\/summary\/?/, '/comps/');
      console.log('\nTrying comps URL:', compsUrl);
      await page.goto(compsUrl, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(e => console.log('Comps URL failed:', e.message));
      await page.waitForTimeout(5000);
      content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
      console.log('\n=== COMPS PAGE ===');
      console.log(content);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
