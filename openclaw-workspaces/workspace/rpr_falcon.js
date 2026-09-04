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

    const addr = '785 Falcon Dr, Port Orange, FL 32127';
    console.log('Searching:', addr);

    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    const searchInput = await page.$('input[type="text"]:visible');
    if (searchInput) {
      await searchInput.click();
      await searchInput.fill('');
      await searchInput.type(addr, { delay: 40 });
      await page.waitForTimeout(3000);

      // Click first suggestion
      await page.evaluate(() => {
        const items = document.querySelectorAll('[class*="keyboard-nav-suggestion"]');
        for (const item of items) {
          if (!item.textContent.includes('listing ID') && !item.textContent.includes('APN')) {
            item.click();
            return;
          }
        }
      });
      await page.waitForTimeout(6000);
      console.log('URL:', page.url());

      // Get full page content
      const content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n--- FULL CONTENT ---\n');
      console.log(content);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
