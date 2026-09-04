const { chromium } = require('playwright');
const { TOTP } = require('totp-generator');

const IMAGE_PATH = '/root/.openclaw/media/inbound/file_3---586e4174-5037-4b57-9a64-4862ac9172f2.jpg';
const TOTP_SECRET = '<REDACTED:CREDENTIAL>';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Going to Google Account signin...');
    await page.goto('https://accounts.google.com/signin');
    await page.waitForTimeout(2000);
    
    console.log('Entering email...');
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    console.log('Entering password...');
    await page.fill('input[type="password"]', 'WilliamStrong2026!HHT');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    
    // Check if 2FA is required
    let content = await page.locator('body').innerText();
    console.log('After password:', content.substring(0, 500));
    
    if (content.includes('2-Step') || content.includes('Verify') || content.includes('code') || page.url().includes('challenge')) {
      console.log('2FA required, generating TOTP...');
      
      // Generate TOTP
      const { otp } = await TOTP.generate(TOTP_SECRET);
      console.log('TOTP code:', otp);
      
      // Find code input
      const codeInput = page.locator('input[type="tel"], input[type="number"], input[type="text"]').first();
      if (await codeInput.isVisible({ timeout: 5000 }).catch(() => false)) {
        await codeInput.fill(otp);
        await page.keyboard.press('Enter');
        await page.waitForTimeout(5000);
        console.log('2FA submitted');
      }
    }
    
    console.log('Current URL:', page.url());
    
    // Navigate to personal info
    console.log('Going to Personal Info...');
    await page.goto('https://myaccount.google.com/personal-info');
    await page.waitForTimeout(5000);
    
    content = await page.locator('body').innerText();
    console.log('Personal info page:', content.substring(0, 600));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile3_personal.png', fullPage: true });
    
    // Check if logged in
    if (!content.includes('Sign in to your account')) {
      console.log('✅ Logged in!');
      
      // Click on Photo
      const photoLink = page.locator('a:has-text("Photo"), button:has-text("Photo")').first();
      if (await photoLink.isVisible({ timeout: 5000 }).catch(() => false)) {
        await photoLink.click();
        await page.waitForTimeout(3000);
        
        await page.screenshot({ path: '/root/.openclaw/workspace/profile3_photo.png', fullPage: true });
      }
      
      // Look for Add/Change photo button
      const addBtn = page.locator('button:has-text("Add profile photo"), button:has-text("Change")').first();
      if (await addBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        await addBtn.click();
        await page.waitForTimeout(3000);
      }
      
      // Look for "From computer"
      content = await page.locator('body').innerText();
      console.log('Looking for upload option:', content.substring(0, 800));
      
      const fromComputer = page.getByText('From computer');
      if (await fromComputer.isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log('Uploading from computer...');
        
        const [fileChooser] = await Promise.all([
          page.waitForEvent('filechooser', { timeout: 15000 }),
          fromComputer.click()
        ]);
        
        await fileChooser.setFiles(IMAGE_PATH);
        await page.waitForTimeout(5000);
        
        await page.screenshot({ path: '/root/.openclaw/workspace/profile3_uploaded.png', fullPage: true });
        
        // Save
        const saveBtn = page.locator('button:has-text("Save as profile photo"), button:has-text("Save")').first();
        if (await saveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          await saveBtn.click();
          await page.waitForTimeout(3000);
        }
        
        console.log('✅ Profile picture uploaded!');
      }
    } else {
      console.log('❌ Still not logged in');
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile3_final.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/profile3_error.png', fullPage: true });
  }

  await browser.close();
})();
