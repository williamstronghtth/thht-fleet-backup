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
    
    console.log('Going to 2FA setup...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification');
    await page.waitForTimeout(3000);
    
    // Click "Add authenticator app"
    console.log('Looking for authenticator option...');
    const addAuthenticator = page.locator('text=Add authenticator app');
    if (await addAuthenticator.isVisible({ timeout: 5000 })) {
      await addAuthenticator.click();
      await page.waitForTimeout(3000);
      
      console.log('On authenticator setup page...');
      const content = await page.locator('body').innerText();
      console.log(content.substring(0, 2000));
      
      // Look for the setup key / secret
      // Google usually shows "Can't scan it?" link to reveal the secret key
      const cantScan = page.locator('text=Can\'t scan');
      if (await cantScan.isVisible({ timeout: 3000 }).catch(() => false)) {
        await cantScan.click();
        await page.waitForTimeout(2000);
        
        const secretContent = await page.locator('body').innerText();
        console.log('\n--- SECRET KEY PAGE ---');
        console.log(secretContent);
        
        // Try to find the secret key (usually a string of letters/numbers)
        const secretMatch = secretContent.match(/([A-Z2-7]{16,32})/);
        if (secretMatch) {
          console.log('\n✅ TOTP SECRET KEY:', secretMatch[1]);
        }
      }
      
      await page.screenshot({ path: '/root/.openclaw/workspace/2fa_setup.png', fullPage: true });
    } else {
      // Maybe need to turn on 2FA first
      console.log('Looking for Turn on button...');
      const turnOn = page.locator('button:has-text("Turn on"), text=Turn on 2-Step Verification');
      if (await turnOn.first().isVisible({ timeout: 3000 })) {
        await turnOn.first().click();
        await page.waitForTimeout(5000);
        
        const newContent = await page.locator('body').innerText();
        console.log('\n--- After clicking Turn On ---');
        console.log(newContent.substring(0, 2000));
        
        await page.screenshot({ path: '/root/.openclaw/workspace/2fa_turnon.png', fullPage: true });
      }
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_error.png', fullPage: true });
  }

  await browser.close();
})();
