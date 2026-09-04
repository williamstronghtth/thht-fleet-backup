const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  try {
    // First, log in to the new account
    console.log('Logging in to william@thehooverhometeam.com...');
    await page.goto('https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // Enter email
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(3000);
    
    // Enter password
    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      await passwordInput.fill('Hoover2026!Wm$trong');
      await page.click('button:has-text("Next")');
      await page.waitForTimeout(5000);
    }
    
    console.log('Logged in, URL:', page.url());
    
    // Now go to Gmail settings to check IMAP/SMTP
    console.log('\nNavigating to Gmail...');
    await page.goto('https://mail.google.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('Gmail URL:', page.url());
    
    // Screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/gmail_new_account.png', fullPage: false });
    
    const content = await page.evaluate(() => document.body.innerText.substring(0, 2000));
    console.log('\n=== GMAIL PAGE ===');
    console.log(content.substring(0, 1000));
    
    // Try to access security settings for app passwords
    console.log('\nNavigating to security settings...');
    await page.goto('https://myaccount.google.com/security', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const securityContent = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('\n=== SECURITY SETTINGS ===');
    console.log(securityContent);
    
    // Look for 2-Step Verification
    const has2FA = securityContent.includes('2-Step Verification');
    console.log('\n2-Step Verification present:', has2FA);
    
    // For Workspace, app passwords might need 2FA first
    // Let's check what options are available

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/error_screenshot.png', fullPage: false });
  } finally {
    await browser.close();
  }
})();
