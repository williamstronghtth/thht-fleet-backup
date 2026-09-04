const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--disable-blink-features=AutomationControlled']
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  const NEW_PASSWORD = '<REDACTED:CREDENTIAL>';

  try {
    console.log('Step 1: Going to Google sign-in...');
    await page.goto('https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin');
    await page.waitForTimeout(2000);
    
    console.log('Step 2: Entering email...');
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(4000);
    
    console.log('Step 3: Entering temporary password...');
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.fill('input[type="password"]', 'williamstrong32!');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    
    console.log('Current URL:', page.url());
    const bodyText = await page.locator('body').innerText();
    
    // Check if we need to change password
    if (bodyText.includes('Create a strong password') || bodyText.includes('Create password')) {
      console.log('Step 4: Setting new password...');
      
      // Find password fields
      const passwordInputs = page.locator('input[type="password"]');
      const count = await passwordInputs.count();
      console.log('Found', count, 'password fields');
      
      if (count >= 2) {
        // Fill new password and confirm
        await passwordInputs.nth(0).fill(NEW_PASSWORD);
        await page.waitForTimeout(300);
        await passwordInputs.nth(1).fill(NEW_PASSWORD);
        await page.waitForTimeout(300);
        
        // Click Next
        await page.click('button:has-text("Next"), div[role="button"]:has-text("Next")');
        await page.waitForTimeout(8000);
        
        console.log('Password changed! URL:', page.url());
        console.log('NEW PASSWORD:', NEW_PASSWORD);
      }
    }
    
    // Check current state
    const currentText = await page.locator('body').innerText();
    console.log('\nCurrent page state:');
    console.log(currentText.substring(0, 800));
    
    // If logged in, go to app passwords
    if (page.url().includes('myaccount') || !currentText.includes('Sign in')) {
      console.log('\nNavigating to app passwords...');
      await page.goto('https://myaccount.google.com/apppasswords');
      await page.waitForTimeout(5000);
      
      const appContent = await page.locator('body').innerText();
      console.log('\nApp passwords page:');
      console.log(appContent.substring(0, 1500));
      
      // Try to create app password
      const appNameInput = page.locator('input').first();
      if (await appNameInput.isVisible({ timeout: 3000 }).catch(() => false)) {
        await appNameInput.fill('OpenClaw Email');
        await page.click('button:has-text("Create")');
        await page.waitForTimeout(4000);
        
        const result = await page.locator('body').innerText();
        console.log('\n--- RESULT ---');
        console.log(result);
        
        const pwMatch = result.match(/([a-z]{4}\s*[a-z]{4}\s*[a-z]{4}\s*[a-z]{4})/i);
        if (pwMatch) {
          console.log('\n✅ APP PASSWORD:', pwMatch[1]);
        }
      }
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/setup_final.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/setup_error.png', fullPage: true });
  }

  await browser.close();
})();
