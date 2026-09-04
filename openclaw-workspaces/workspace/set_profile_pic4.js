const { chromium } = require('playwright');

const IMAGE_PATH = '/root/.openclaw/media/inbound/file_3---586e4174-5037-4b57-9a64-4862ac9172f2.jpg';
const SMS_CODE = '024552';

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
    
    // Enter SMS code
    console.log('Entering SMS verification code...');
    const codeInput = page.locator('input[type="tel"], input').first();
    await codeInput.fill(SMS_CODE);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    
    console.log('Current URL:', page.url());
    
    // Go to personal info
    console.log('Going to Personal Info...');
    await page.goto('https://myaccount.google.com/personal-info');
    await page.waitForTimeout(5000);
    
    let content = await page.locator('body').innerText();
    console.log('Page content:', content.substring(0, 600));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile4_info.png', fullPage: true });
    
    if (!content.includes('sign in to your account')) {
      console.log('✅ Logged in! Looking for Photo...');
      
      // Click Photo
      await page.getByText('Photo').first().click();
      await page.waitForTimeout(3000);
      
      content = await page.locator('body').innerText();
      console.log('Photo section:', content.substring(0, 800));
      await page.screenshot({ path: '/root/.openclaw/workspace/profile4_photo.png', fullPage: true });
      
      // Click Add/Change
      const addBtn = page.locator('button:has-text("Add profile photo"), button:has-text("Change")').first();
      if (await addBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        await addBtn.click();
        await page.waitForTimeout(3000);
      }
      
      // Click From computer
      const fromComputer = page.getByText('From computer');
      if (await fromComputer.isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log('Uploading image...');
        
        const [fileChooser] = await Promise.all([
          page.waitForEvent('filechooser', { timeout: 15000 }),
          fromComputer.click()
        ]);
        
        await fileChooser.setFiles(IMAGE_PATH);
        await page.waitForTimeout(5000);
        
        await page.screenshot({ path: '/root/.openclaw/workspace/profile4_uploaded.png', fullPage: true });
        
        // Save
        const saveBtn = page.locator('button:has-text("Save as profile photo"), button:has-text("Save")').first();
        if (await saveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          await saveBtn.click();
          await page.waitForTimeout(3000);
        }
        
        console.log('✅ Profile picture updated!');
      }
    } else {
      console.log('❌ Not logged in');
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile4_final.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/profile4_error.png', fullPage: true });
  }

  await browser.close();
})();
