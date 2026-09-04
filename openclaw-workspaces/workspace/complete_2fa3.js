const { chromium } = require('playwright');
const OTPAuth = require('otplib');

const TOTP_SECRET = '<REDACTED:CREDENTIAL>';

// Generate TOTP code
function generateTOTP(secret) {
  const totp = new OTPAuth.totp.TOTP({
    secret: <REDACTED:CREDENTIAL>(secret),
    algorithm: 'SHA1',
    digits: 6,
    period: 30
  });
  return OTPAuth.authenticator.generate(secret);
}

(async () => {
  // First test TOTP generation
  try {
    const testCode = OTPAuth.authenticator.generate(TOTP_SECRET);
    console.log('Test TOTP code:', testCode);
  } catch (e) {
    console.log('TOTP test error:', e.message);
  }

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
    
    // Generate TOTP code
    const totpCode = OTPAuth.authenticator.generate(TOTP_SECRET);
    console.log('Generated TOTP code:', totpCode);
    
    // Find code input and enter code
    console.log('Looking for code input...');
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
    
    // Check if we need to complete the setup
    if (content.includes('Done') || content.includes('Turn on')) {
      // Click Done or Turn on
      const doneBtn = page.locator('button:has-text("Done"), button:has-text("Turn on")').first();
      if (await doneBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await doneBtn.click();
        await page.waitForTimeout(3000);
      }
    }
    
    // Now get app password
    console.log('\nNavigating to app passwords...');
    await page.goto('https://myaccount.google.com/apppasswords');
    await page.waitForTimeout(5000);
    
    content = await page.locator('body').innerText();
    console.log('App passwords page:', content.substring(0, 1000));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/app_passwords_page2.png', fullPage: true });
    
    // Create app password
    const appInput = page.locator('input').first();
    if (await appInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('Creating app password...');
      await appInput.fill('OpenClaw Email');
      await page.locator('button:has-text("Create")').click();
      await page.waitForTimeout(4000);
      
      content = await page.locator('body').innerText();
      console.log('\n--- APP PASSWORD RESULT ---');
      console.log(content);
      
      const pwMatch = content.match(/([a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4})/i);
      if (pwMatch) {
        console.log('\n✅ APP PASSWORD:', pwMatch[1]);
      }
      
      await page.screenshot({ path: '/root/.openclaw/workspace/app_password_final.png', fullPage: true });
    } else {
      console.log('App password input not found. Page content:', content.substring(0, 500));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_error_final2.png', fullPage: true });
  }

  await browser.close();
})();
