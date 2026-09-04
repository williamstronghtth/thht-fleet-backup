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
    
    console.log('Going to 2FA authenticator setup...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome');
    await page.waitForTimeout(3000);
    
    // Click through the setup flow
    console.log('Looking for setup button...');
    
    // Try clicking "Set up authenticator" or similar
    const setupBtn = page.locator('button:has-text("Set up"), a:has-text("Set up authenticator"), text=Set up authenticator');
    if (await setupBtn.first().isVisible({ timeout: 5000 })) {
      console.log('Found setup button, clicking...');
      await setupBtn.first().click();
      await page.waitForTimeout(5000);
    }
    
    let content = await page.locator('body').innerText();
    console.log('\n--- CURRENT PAGE ---');
    console.log(content.substring(0, 1500));
    
    // Look for QR code page or "Can't scan it?" link
    if (content.includes('scan') || content.includes('QR') || content.includes('barcode')) {
      console.log('\nLooking for manual setup option...');
      
      // Click "Can't scan it?" to get the secret key
      const cantScan = page.locator('button:has-text("Can\'t scan"), a:has-text("Can\'t scan"), text=Can\'t scan');
      if (await cantScan.first().isVisible({ timeout: 3000 }).catch(() => false)) {
        await cantScan.first().click();
        await page.waitForTimeout(2000);
      }
      
      content = await page.locator('body').innerText();
      console.log('\n--- AFTER CANT SCAN ---');
      console.log(content);
      
      // Look for the secret key
      const secretMatch = content.match(/([A-Z2-7]{16,32})/g);
      if (secretMatch) {
        console.log('\n✅ POSSIBLE SECRET KEYS:');
        secretMatch.forEach(s => console.log('  ', s));
      }
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_setup2.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_error2.png', fullPage: true });
  }

  await browser.close();
})();
