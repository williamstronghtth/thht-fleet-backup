const { chromium } = require('playwright');
const { TOTP } = require('totp-generator');

const TOTP_SECRET = '<REDACTED:CREDENTIAL>';

(async () => {
  // Test TOTP generation
  const { otp: testCode } = TOTP.generate(TOTP_SECRET);
  console.log('Test TOTP code:', testCode);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Logging in...');
    await page.goto('https://accounts.google.com/signin');
    await page.waitForTimeout(2000);
    
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    await page.fill('input[type="password"]', 'WilliamStrong2026!HHT');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    
    // Go to authenticator setup
    console.log('Going to authenticator setup...');
    await page.goto('https://myaccount.google.com/signinoptions/two-step-verification');
    await page.waitForTimeout(3000);
    
    // Click Add authenticator app
    await page.getByText('Add authenticator app').click();
    await page.waitForTimeout(3000);
    
    // Click Set up authenticator
    await page.getByText('Set up authenticator').click();
    await page.waitForTimeout(3000);
    
    // Click Next to go to code entry
    console.log('Clicking Next...');
    await page.locator('button:has-text("Next")').last().click();
    await page.waitForTimeout(3000);
    
    // Generate fresh TOTP code right before entering
    const { otp: totpCode } = TOTP.generate(TOTP_SECRET);
    console.log('Generated TOTP code:', totpCode);
    
    // Find code input and enter code
    console.log('Entering code...');
    const codeInput = page.locator('input').first();
    await codeInput.fill(totpCode);
    await page.waitForTimeout(500);
    
    // Click Verify
    console.log('Clicking Verify...');
    await page.locator('button:has-text("Verify")').click();
    await page.waitForTimeout(5000);
    
    let content = await page.locator('body').innerText();
    console.log('\n--- AFTER VERIFICATION ---');
    console.log(content.substring(0, 1500));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_verified.png', fullPage: true });
    
    // Check if we need to click Done or Turn on
    const doneBtn = page.locator('button:has-text("Done"), button:has-text("Turn on")').first();
    if (await doneBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('Clicking Done/Turn on...');
      await doneBtn.click();
      await page.waitForTimeout(3000);
    }
    
    // Now get app password
    console.log('\nNavigating to app passwords...');
    await page.goto('https://myaccount.google.com/apppasswords');
    await page.waitForTimeout(5000);
    
    content = await page.locator('body').innerText();
    console.log('App passwords page:', content.substring(0, 1200));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/app_passwords_page2.png', fullPage: true });
    
    // Create app password
    if (!content.includes('not available')) {
      const appInput = page.locator('input').first();
      if (await appInput.isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log('Creating app password...');
        await appInput.fill('OpenClaw Email');
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(5000);
        
        content = await page.locator('body').innerText();
        console.log('\n--- APP PASSWORD RESULT ---');
        console.log(content);
        
        const pwMatch = content.match(/([a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4})/i);
        if (pwMatch) {
          console.log('\n✅ APP PASSWORD:', pwMatch[1]);
        }
        
        await page.screenshot({ path: '/root/.openclaw/workspace/app_password_created.png', fullPage: true });
      }
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/error.png', fullPage: true });
    const content = await page.locator('body').innerText().catch(() => '');
    console.log('Page on error:', content.substring(0, 800));
  }

  await browser.close();
})();
