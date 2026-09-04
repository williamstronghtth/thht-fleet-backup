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

  try {
    console.log('Step 1: Going to Google sign-in...');
    await page.goto('https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin');
    await page.waitForTimeout(2000);
    
    console.log('Step 2: Entering email...');
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(4000);
    
    console.log('Step 3: Entering password...');
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.fill('input[type="password"]', 'williamstrong32!');
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    
    console.log('Step 4: Waiting for login result...');
    await page.waitForTimeout(8000);
    
    console.log('Current URL after login:', page.url());
    
    const bodyText = await page.locator('body').innerText();
    
    // Check if we're logged in
    if (page.url().includes('myaccount') || page.url().includes('mail.google') || 
        (bodyText.includes('Google Account') && !bodyText.includes('Enter your password'))) {
      console.log('\n✅ LOGIN SUCCESSFUL!');
      
      // Go to app passwords
      console.log('\nNavigating to app passwords...');
      await page.goto('https://myaccount.google.com/apppasswords');
      await page.waitForTimeout(5000);
      
      console.log('App passwords URL:', page.url());
      const appContent = await page.locator('body').innerText();
      
      if (appContent.includes('App passwords') || appContent.includes('app name')) {
        console.log('On app passwords page!');
        
        // Find and fill the app name input
        const inputs = page.locator('input');
        const inputCount = await inputs.count();
        console.log('Found', inputCount, 'input fields');
        
        for (let i = 0; i < inputCount; i++) {
          const input = inputs.nth(i);
          const type = await input.getAttribute('type');
          const aria = await input.getAttribute('aria-label');
          console.log(`Input ${i}: type=${type}, aria=${aria}`);
        }
        
        // Try to fill the app name
        const appNameInput = page.locator('input').first();
        await appNameInput.fill('OpenClaw Email');
        await page.waitForTimeout(500);
        
        // Click Create
        await page.click('button:has-text("Create")');
        await page.waitForTimeout(4000);
        
        // Get the password
        const resultContent = await page.locator('body').innerText();
        console.log('\n--- RESULT PAGE ---');
        console.log(resultContent);
        
        // Find the app password (16 chars, often with spaces)
        const pwMatch = resultContent.match(/([a-z]{4}\s*[a-z]{4}\s*[a-z]{4}\s*[a-z]{4})/i);
        if (pwMatch) {
          console.log('\n✅ APP PASSWORD:', pwMatch[1]);
        }
      } else {
        console.log('Not on app passwords page:');
        console.log(appContent.substring(0, 1500));
      }
      
    } else {
      console.log('\n❌ Login failed. Page content:');
      console.log(bodyText.substring(0, 1000));
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/setup_result.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/setup_error.png', fullPage: true });
  }

  await browser.close();
})();
