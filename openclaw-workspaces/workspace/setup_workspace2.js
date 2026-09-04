const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  try {
    const setupUrl = 'https://accounts.google.com/RP?c=CPqvpaOhkrO74QEQsNGWrt2QrJUu&uc=ac&hl=en&continue=https://workspace.google.com/dashboard&fc=1&flowName=GlifWebSignIn';
    
    console.log('Step 1: Navigating to setup URL...');
    await page.goto(setupUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    // Accept terms if on speedbump page
    const confirmBtn = await page.$('#confirm');
    if (confirmBtn) {
      console.log('Found confirm button, clicking...');
      await confirmBtn.click();
      await page.waitForTimeout(5000);
    }
    
    console.log('Step 2: Page URL:', page.url());
    
    // Screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/workspace_setup2.png', fullPage: false });
    
    // Get page content
    let content = await page.evaluate(() => document.body.innerText.substring(0, 4000));
    console.log('\n=== PAGE CONTENT ===');
    console.log(content);

    // Look for password field
    const passwordInput = await page.$('input[type="password"], input[name="password"], input[name="Passwd"]');
    if (passwordInput) {
      console.log('\nFound password input! Setting password...');
      
      // Generate a secure password
      const newPassword = '<REDACTED:CREDENTIAL>';
      
      // Fill password
      await passwordInput.fill(newPassword);
      await page.waitForTimeout(1000);
      
      // Look for confirm password field
      const confirmPass = await page.$('input[name="ConfirmPasswd"], input[name="confirmpassword"], input[aria-label*="Confirm"]');
      if (confirmPass) {
        await confirmPass.fill(newPassword);
        await page.waitForTimeout(1000);
      }
      
      // Click next/submit
      const nextBtn = await page.$('button:has-text("Next"), button:has-text("Create"), input[type="submit"]');
      if (nextBtn) {
        console.log('Clicking submit...');
        await nextBtn.click();
        await page.waitForTimeout(5000);
      }
      
      console.log('After password submit, URL:', page.url());
      await page.screenshot({ path: '/root/.openclaw/workspace/workspace_setup3.png', fullPage: false });
      
      content = await page.evaluate(() => document.body.innerText.substring(0, 3000));
      console.log('\n=== AFTER PASSWORD ===');
      console.log(content);
    } else {
      console.log('No password input found yet');
      
      // List all inputs
      const inputs = await page.$$eval('input:visible', els => els.map(e => ({
        type: e.type,
        name: e.name,
        id: e.id,
        placeholder: e.placeholder
      })));
      console.log('\nVisible inputs:', JSON.stringify(inputs, null, 2));
      
      // List buttons
      const buttons = await page.$$eval('button, input[type="submit"]', els => 
        els.filter(e => e.offsetParent !== null).map(e => e.textContent?.trim() || e.value));
      console.log('Buttons:', buttons);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
