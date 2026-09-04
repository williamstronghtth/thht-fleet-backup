const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Login to Google Account
  console.log('Logging into Google Account...');
  await page.goto('https://myaccount.google.com/security');
  await page.waitForTimeout(2000);
  
  // Check if we need to login
  if (await page.locator('input[type="email"]').isVisible()) {
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.click('#identifierNext');
    await page.waitForTimeout(3000);
    
    await page.fill('input[type="password"]', 'n7J>=A8MbG*Y5mD&');
    await page.click('#passwordNext');
    await page.waitForTimeout(5000);
  }

  // Navigate to App passwords page
  console.log('Navigating to App Passwords...');
  await page.goto('https://myaccount.google.com/apppasswords');
  await page.waitForTimeout(3000);

  // Take screenshot to see what's there
  await page.screenshot({ path: '/root/.openclaw/workspace/app_password_page.png', fullPage: true });
  console.log('Screenshot saved to app_password_page.png');

  // Try to create app password
  // First check if there's a text input for app name
  const pageContent = await page.content();
  console.log('Page URL:', page.url());
  
  // Look for the app name input field
  const inputField = page.locator('input[aria-label="App name"]');
  if (await inputField.isVisible()) {
    console.log('Found app name input, creating password...');
    await inputField.fill('OpenClaw Email');
    await page.waitForTimeout(500);
    
    // Click Create button
    await page.click('button:has-text("Create")');
    await page.waitForTimeout(3000);
    
    // Get the generated password
    await page.screenshot({ path: '/root/.openclaw/workspace/app_password_result.png', fullPage: true });
    
    // Try to find the password text
    const passwordText = await page.locator('div[class*="password"], span[class*="code"], div:has-text("Your app password")').textContent();
    console.log('App password info:', passwordText);
  } else {
    console.log('App name input not found. Current page state saved to screenshot.');
    // Print visible text for debugging
    const bodyText = await page.locator('body').innerText();
    console.log('Page text:', bodyText.substring(0, 1000));
  }

  await browser.close();
})();
