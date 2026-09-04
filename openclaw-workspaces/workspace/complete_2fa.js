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
    
    // Click Next to go to code entry
    console.log('Clicking Next...');
    await page.getByText('Next').click();
    await page.waitForTimeout(3000);
    
    // Generate TOTP code
    const totpCode = authenticator.generate(TOTP_SECRET.toUpperCase());
    console.log('Generated TOTP code:', totpCode);
    
    // Get page content to see what we have
    let content = await page.locator('body').innerText();
    console.log('\nCurrent page:', content.substring(0, 800));
    
    // Find code input and enter code
    const codeInput = page.locator('input[type="tel"], input[type="text"]').first();
    if (await codeInput.isVisible({ timeout: 5000 })) {
      console.log('\nEntering TOTP code...');
      await codeInput.fill(totpCode);
      await page.waitForTimeout(500);
      
      // Click Verify or Next
      const verifyBtn = page.getByText('Verify');
      if (await verifyBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await verifyBtn.click();
      } else {
        await page.getByText('Next').click();
      }
      await page.waitForTimeout(5000);
      
      content = await page.locator('body').innerText();
      console.log('\n--- AFTER VERIFICATION ---');
      console.log(content.substring(0, 1500));
      
      // Check if 2FA is now enabled
      if (content.includes('Turn off') || content.includes('2-Step Verification is on')) {
        console.log('\n✅ 2FA ENABLED SUCCESSFULLY!');
        
        // Now get app password
        console.log('\nGetting app password...');
        await page.goto('https://myaccount.google.com/apppasswords');
        await page.waitForTimeout(5000);
        
        content = await page.locator('body').innerText();
        console.log('App passwords page:', content.substring(0, 1000));
        
        // Enter app name
        const appNameInput = page.locator('input').first();
        if (await appNameInput.isVisible({ timeout: 5000 })) {
          await appNameInput.fill('OpenClaw Email');
          await page.click('button:has-text("Create")');
          await page.waitForTimeout(4000);
          
          content = await page.locator('body').innerText();
          console.log('\n--- APP PASSWORD RESULT ---');
          console.log(content);
          
          // Find the app password
          const pwMatch = content.match(/([a-z]{4}\s*[a-z]{4}\s*[a-z]{4}\s*[a-z]{4})/i);
          if (pwMatch) {
            console.log('\n✅ APP PASSWORD:', pwMatch[1]);
          }
        }
      }
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_complete.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/2fa_complete_error.png', fullPage: true });
    const content = await page.locator('body').innerText().catch(() => '');
    console.log('Page on error:', content.substring(0, 1000));
  }

  await browser.close();
})();
