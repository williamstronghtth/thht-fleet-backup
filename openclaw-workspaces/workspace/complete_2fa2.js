const { chromium } = require('playwright');
const { authenticator } = require('otplib');

const TOTP_SECRET = '<REDACTED:CREDENTIAL>';

(async () => {
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
    
    // Screenshot the QR code dialog
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_qr_dialog.png', fullPage: true });
    
    // Click the dialog's Next button (inside the modal)
    console.log('Clicking Next on QR dialog...');
    // Find the button inside the dialog that says Next
    const nextButtons = page.locator('button:has-text("Next")');
    const count = await nextButtons.count();
    console.log('Found', count, 'Next buttons');
    
    // Click the last one (should be in the dialog)
    await nextButtons.last().click();
    await page.waitForTimeout(3000);
    
    // Check current state
    let content = await page.locator('body').innerText();
    console.log('\nAfter clicking Next:', content.substring(0, 1000));
    
    // Generate TOTP code
    const totpCode = authenticator.generate(TOTP_SECRET.toUpperCase());
    console.log('\nGenerated TOTP code:', totpCode);
    
    // Look for code input
    const codeInput = page.locator('input[type="tel"], input[type="number"], input[type="text"]').first();
    if (await codeInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      console.log('Found code input, entering code...');
      await codeInput.fill(totpCode);
      await page.waitForTimeout(500);
      
      // Click Verify
      const verifyBtn = page.locator('button:has-text("Verify")');
      if (await verifyBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await verifyBtn.click();
      } else {
        await page.locator('button:has-text("Next")').last().click();
      }
      await page.waitForTimeout(5000);
      
      content = await page.locator('body').innerText();
      console.log('\n--- AFTER VERIFICATION ---');
      console.log(content.substring(0, 1500));
    } else {
      console.log('Code input not found');
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_result.png', fullPage: true });
    
    // Check if 2FA setup completed
    if (content.includes('Turn off') || content.includes('authenticator app') || content.includes('Authenticator')) {
      console.log('\n✅ 2FA setup appears complete!');
      
      // Now get app password
      console.log('\nNavigating to app passwords...');
      await page.goto('https://myaccount.google.com/apppasswords');
      await page.waitForTimeout(5000);
      
      content = await page.locator('body').innerText();
      console.log('App passwords page:', content.substring(0, 1000));
      
      await page.screenshot({ path: '/root/.openclaw/workspace/app_passwords_after_2fa.png', fullPage: true });
      
      // Try to create app password
      const appInput = page.locator('input').first();
      if (await appInput.isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log('Creating app password...');
        await appInput.fill('OpenClaw Email');
        await page.click('button:has-text("Create")');
        await page.waitForTimeout(4000);
        
        content = await page.locator('body').innerText();
        console.log('\n--- APP PASSWORD ---');
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
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_error_final.png', fullPage: true });
    const content = await page.locator('body').innerText().catch(() => '');
    console.log('Page on error:', content.substring(0, 1000));
  }

  await browser.close();
})();
