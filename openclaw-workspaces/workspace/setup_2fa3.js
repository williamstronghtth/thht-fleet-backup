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
    
    console.log('Going to 2FA setup page...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification');
    await page.waitForTimeout(3000);
    
    let content = await page.locator('body').innerText();
    console.log('Current page:', content.substring(0, 500));
    
    // Click Add authenticator app
    console.log('\nClicking Add authenticator...');
    await page.getByText('Add authenticator app').click();
    await page.waitForTimeout(3000);
    
    content = await page.locator('body').innerText();
    console.log('\nAuthenticator page:', content.substring(0, 800));
    
    // Click Set up authenticator
    console.log('\nClicking Set up authenticator...');
    await page.getByText('Set up authenticator').click();
    await page.waitForTimeout(5000);
    
    content = await page.locator('body').innerText();
    console.log('\nSetup page:', content.substring(0, 1500));
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_qr.png', fullPage: true });
    
    // Try to find "Can't scan it?" link
    const cantScanVisible = await page.getByText("Can't scan it").isVisible().catch(() => false);
    if (cantScanVisible) {
      console.log('\nClicking Can\'t scan it...');
      await page.getByText("Can't scan it").click();
      await page.waitForTimeout(2000);
      
      content = await page.locator('body').innerText();
      console.log('\n--- SECRET KEY PAGE ---');
      console.log(content);
      
      // Extract secret key
      const secretMatch = content.match(/([A-Z2-7]{16,32})/g);
      if (secretMatch) {
        console.log('\n✅ TOTP SECRET KEY CANDIDATES:');
        secretMatch.forEach(s => console.log('  ', s));
      }
      
      await page.screenshot({ path: '/root/.openclaw/workspace/2fa_secret.png', fullPage: true });
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_error3.png', fullPage: true });
    const content = await page.locator('body').innerText().catch(() => '');
    console.log('Page content on error:', content.substring(0, 1000));
  }

  await browser.close();
})();
