const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Login to Google Account
    console.log('Logging into Google Account...');
    await page.goto('https://accounts.google.com');
    await page.waitForTimeout(2000);
    
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.click('#identifierNext');
    await page.waitForTimeout(3000);
    
    await page.fill('input[type="password"]', 'n7J>=A8MbG*Y5mD&');
    await page.click('#passwordNext');
    
    // Wait for login to complete
    console.log('Waiting for login to complete...');
    await page.waitForURL('**/myaccount.google.com/**', { timeout: 15000 });
    console.log('Logged in! Current URL:', page.url());
    
    // Now navigate to app passwords
    console.log('Navigating to App Passwords...');
    await page.goto('https://myaccount.google.com/apppasswords');
    await page.waitForTimeout(5000);
    
    console.log('App passwords page URL:', page.url());
    await page.screenshot({ path: '/root/.openclaw/workspace/app_password_page2.png', fullPage: true });
    
    // Check if there's an input for app name
    const inputField = page.locator('input[aria-label="App name"]');
    if (await inputField.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('Found app name input, creating password...');
      await inputField.fill('OpenClaw Email');
      await page.waitForTimeout(500);
      await page.click('button:has-text("Create")');
      await page.waitForTimeout(3000);
      await page.screenshot({ path: '/root/.openclaw/workspace/app_password_result.png', fullPage: true });
      
      // Try to extract the password
      const allText = await page.locator('body').innerText();
      console.log('Page content after create:', allText.substring(0, 2000));
    } else {
      // Print page content for debugging
      const bodyText = await page.locator('body').innerText();
      console.log('Page text:', bodyText.substring(0, 2000));
    }
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/app_password_error.png', fullPage: true });
    const bodyText = await page.locator('body').innerText();
    console.log('Page text on error:', bodyText.substring(0, 1500));
  }

  await browser.close();
})();
