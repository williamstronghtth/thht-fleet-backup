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
    console.log('Current URL:', page.url());
    
    // Wait for password field
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.fill('input[type="password"]', 'n7J>=A8MbG*Y5mD&');
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    
    console.log('Step 4: Waiting for login result...');
    await page.waitForTimeout(8000);
    
    console.log('Current URL after login:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/login_result.png', fullPage: true });
    
    const bodyText = await page.locator('body').innerText();
    console.log('\n--- PAGE CONTENT ---');
    console.log(bodyText.substring(0, 1500));
    console.log('--- END ---');
    
    // Check if we're logged in
    if (page.url().includes('myaccount') || bodyText.includes('Google Account') && !bodyText.includes('Sign in')) {
      console.log('\n✅ LOGIN SUCCESSFUL!');
      
      // Try to go to app passwords
      console.log('Navigating to app passwords...');
      await page.goto('https://myaccount.google.com/apppasswords');
      await page.waitForTimeout(5000);
      
      const appPwContent = await page.locator('body').innerText();
      console.log('\n--- APP PASSWORDS PAGE ---');
      console.log(appPwContent.substring(0, 2000));
      
      await page.screenshot({ path: '/root/.openclaw/workspace/app_passwords_page.png', fullPage: true });
    } else {
      console.log('\n❌ Login appears to have failed or needs additional verification');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/login_error.png', fullPage: true });
  }

  await browser.close();
})();
