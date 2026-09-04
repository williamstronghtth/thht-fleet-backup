const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Login to Google Account
    console.log('Logging into Google Account...');
    await page.goto('https://accounts.google.com/signin');
    await page.waitForTimeout(2000);
    
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.click('#identifierNext');
    await page.waitForTimeout(3000);
    
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.fill('input[type="password"]', 'n7J>=A8MbG*Y5mD&');
    await page.click('#passwordNext');
    
    // Wait for redirect after login
    console.log('Waiting for login to complete...');
    await page.waitForTimeout(8000);
    console.log('Current URL after login:', page.url());
    
    // Navigate directly to app passwords
    console.log('Navigating to App Passwords...');
    await page.goto('https://myaccount.google.com/apppasswords');
    await page.waitForTimeout(5000);
    
    console.log('App passwords page URL:', page.url());
    
    // Check if we're on the right page
    const pageContent = await page.locator('body').innerText();
    
    if (pageContent.includes('App passwords')) {
      console.log('On app passwords page!');
      
      // Look for input field
      const inputSelector = 'input[aria-label="App name"], input[placeholder*="app"], input[type="text"]';
      const input = page.locator(inputSelector).first();
      
      if (await input.isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log('Found input field, creating app password...');
        await input.fill('OpenClaw Email');
        await page.waitForTimeout(500);
        
        // Click Create button
        const createBtn = page.locator('button:has-text("Create"), button:has-text("CREATE")').first();
        await createBtn.click();
        await page.waitForTimeout(4000);
        
        // Get the generated password - it's usually shown in a modal or highlighted text
        const newContent = await page.locator('body').innerText();
        console.log('\n--- PAGE CONTENT AFTER CREATE ---');
        console.log(newContent);
        console.log('--- END ---\n');
        
        // Try to find the password (usually 16 chars with spaces)
        const passwordMatch = newContent.match(/[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}/i);
        if (passwordMatch) {
          console.log('\n✅ APP PASSWORD FOUND:', passwordMatch[0]);
        }
      } else {
        console.log('Input field not found. Page content:');
        console.log(pageContent.substring(0, 2000));
      }
    } else if (pageContent.includes('Sign in')) {
      console.log('Still on sign-in page. Login may have failed.');
      console.log(pageContent.substring(0, 1000));
    } else {
      console.log('Unknown page state:');
      console.log(pageContent.substring(0, 2000));
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/app_password_final.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/app_password_error.png', fullPage: true });
  }

  await browser.close();
})();
