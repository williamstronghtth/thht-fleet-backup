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
    await page.goto(setupUrl, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Accept terms if on speedbump page
    const confirmBtn = await page.$('#confirm');
    if (confirmBtn) {
      console.log('Accepting terms...');
      await confirmBtn.click();
      await page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {});
      await page.waitForTimeout(3000);
    }
    
    console.log('Step 2: On password page, URL:', page.url());
    
    // Get all password inputs
    const passwordInputs = await page.$$('input[type="password"]');
    console.log(`Found ${passwordInputs.length} password inputs`);
    
    const newPassword = '<REDACTED:CREDENTIAL>';
    
    if (passwordInputs.length >= 2) {
      // First input is "Create password", second is "Confirm password"
      console.log('Filling first password field...');
      await passwordInputs[0].click();
      await passwordInputs[0].fill(newPassword);
      await page.waitForTimeout(500);
      
      console.log('Filling confirm password field...');
      await passwordInputs[1].click();
      await passwordInputs[1].fill(newPassword);
      await page.waitForTimeout(500);
      
      // Screenshot before submit
      await page.screenshot({ path: '/root/.openclaw/workspace/workspace_before_submit.png', fullPage: false });
      
      // Find and click submit button
      // Google uses various button texts
      const submitBtn = await page.$('button[type="submit"], button:has-text("Change password"), button:has-text("Save"), button:has-text("Next")');
      
      if (submitBtn) {
        console.log('Clicking submit button...');
        await submitBtn.click();
      } else {
        // Try pressing Enter
        console.log('No submit button found, pressing Enter...');
        await page.keyboard.press('Enter');
      }
      
      await page.waitForTimeout(8000);
      console.log('After submit, URL:', page.url());
      
      // Screenshot after
      await page.screenshot({ path: '/root/.openclaw/workspace/workspace_after_submit.png', fullPage: false });
      
      const content = await page.evaluate(() => document.body.innerText.substring(0, 2000));
      console.log('\n=== RESULT ===');
      console.log(content);
      
      if (page.url().includes('workspace.google.com') || page.url().includes('myaccount')) {
        console.log('\n✅ SUCCESS! Account set up.');
        console.log('Email: william@thehooverhometeam.com');
        console.log('Password:', newPassword);
      }
      
    } else if (passwordInputs.length === 1) {
      console.log('Only one password field, filling it...');
      await passwordInputs[0].fill(newPassword);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(5000);
      
      // Check for confirm field now
      const confirmInput = await page.$('input[type="password"]');
      if (confirmInput) {
        await confirmInput.fill(newPassword);
        await page.keyboard.press('Enter');
        await page.waitForTimeout(8000);
      }
      
      console.log('Final URL:', page.url());
    } else {
      console.log('No password inputs found!');
      const content = await page.evaluate(() => document.body.innerText.substring(0, 2000));
      console.log(content);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
