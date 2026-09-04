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

    // Go directly to property search with listing ID
    await page.goto('https://www.narrpr.com/properties/search?scid=262011377', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);

    // Click on the 785 Falcon Dr listing
    await page.evaluate(() => {
      const rows = document.querySelectorAll('tr, [class*="property-row"], [class*="result-item"]');
      for (const row of rows) {
        if (row.textContent.includes('785 Falcon Dr')) {
          row.click();
          return;
        }
      }
      // Try clicking on address link
      const links = document.querySelectorAll('a');
      for (const link of links) {
        if (link.textContent.includes('785 Falcon Dr')) {
          link.click();
          return;
        }
      }
    });
    await page.waitForTimeout(6000);
    console.log('URL:', page.url());

    // Get full page content
    const content = await page.evaluate(() => document.body.innerText.substring(0, 12000));
    console.log('\n--- PROPERTY DETAILS ---\n');
    console.log(content);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
