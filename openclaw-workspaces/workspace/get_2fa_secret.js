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
    
    // Go directly to authenticator setup
    console.log('Going to authenticator setup...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification');
    await page.waitForTimeout(3000);
    
    // Click Add authenticator app
    await page.getByText('Add authenticator app').click();
    await page.waitForTimeout(3000);
    
    // Click Set up authenticator
    await page.getByText('Set up authenticator').click();
    await page.waitForTimeout(3000);
    
    // Now click "Can't scan it?"
    console.log('Clicking Can\'t scan it...');
    await page.getByText("Can't scan it?").click();
    await page.waitForTimeout(3000);
    
    // Get the full page content
    const content = await page.locator('body').innerText();
    console.log('\n=== SECRET KEY PAGE ===');
    console.log(content);
    console.log('=== END ===\n');
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_secret_key.png', fullPage: true });
    
    // Try to find the key in the text
    // Google TOTP secrets are base32 encoded, typically 16-32 chars
    const matches = content.match(/[A-Z2-7]{16,32}/g);
    if (matches) {
      console.log('\n✅ FOUND SECRET KEY CANDIDATES:');
      matches.forEach(m => console.log('  ', m));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_secret_error.png', fullPage: true });
  }

  await browser.close();
})();
