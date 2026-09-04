const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Go to RPR login
    console.log('Navigating to RPR...');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'networkidle', timeout: 30000 });
    console.log('Page title:', await page.title());
    console.log('Current URL:', page.url());

    // Look for login fields
    const html = await page.content();
    
    // Try to find email/login field
    const emailField = await page.$('input[type="email"], input[name="email"], input[id*="email"], input[id*="user"], input[name*="user"], input[placeholder*="email"], input[placeholder*="Email"]');
    if (emailField) {
      console.log('Found email field, filling in...');
      await emailField.fill('ch@thehooverhometeam.com');
    } else {
      console.log('No email field found. Looking for login button/link...');
      const loginLink = await page.$('a[href*="login"], button:has-text("Log In"), a:has-text("Log In"), button:has-text("Sign In"), a:has-text("Sign In")');
      if (loginLink) {
        console.log('Found login link, clicking...');
        await loginLink.click();
        await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
        console.log('After click URL:', page.url());
        console.log('After click title:', await page.title());
      }
    }
    
    // Take a screenshot of what we see
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_screenshot.png', fullPage: false });
    console.log('Screenshot saved');
    
    // Get page text content
    const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 2000));
    console.log('Page content:', bodyText);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
