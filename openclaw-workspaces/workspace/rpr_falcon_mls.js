const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in!\n');

    // Search by MLS listing ID
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    const searchInput = await page.$('input[type="text"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type('1222522', { delay: 40 });
      await page.waitForTimeout(3000);
      
      // Look for "Find all listings matching this listing ID" option
      const clicked = await page.evaluate(() => {
        const items = document.querySelectorAll('[class*="keyboard-nav-suggestion"], [class*="dropdown-link"]');
        for (const item of items) {
          if (item.textContent.includes('listing ID')) {
            item.click();
            return 'clicked listing ID option';
          }
        }
        return 'not found';
      });
      console.log('Listing ID search:', clicked);
      await page.waitForTimeout(6000);
      console.log('URL:', page.url());

      // Get full page content
      const content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n--- CONTENT ---\n');
      console.log(content);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
