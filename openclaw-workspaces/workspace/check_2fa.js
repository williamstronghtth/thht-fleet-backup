const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Logging in...');
    await page.goto('https://accounts.google.com/signin');
    await page.waitForTimeout(2000);
    
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    await page.fill('input[type="password"]', 'WilliamStrong2026!HHT');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    
    console.log('Checking 2FA status...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification');
    await page.waitForTimeout(5000);
    
    const content = await page.locator('body').innerText();
    console.log('\n--- 2FA PAGE ---');
    console.log(content.substring(0, 2000));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_status.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
  }

  await browser.close();
})();
