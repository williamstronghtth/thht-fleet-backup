const { chromium } = require('playwright');

const IMAGE_PATH = '/root/.openclaw/media/inbound/file_3---586e4174-5037-4b57-9a64-4862ac9172f2.jpg';
const SMS_CODE = '868337';

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
    await page.waitForTimeout(4000);
    
    // Enter SMS code immediately
    console.log('Entering SMS code:', SMS_CODE);
    const codeInput = page.locator('input').first();
    await codeInput.fill(SMS_CODE);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(6000);
    
    console.log('URL after 2FA:', page.url());
    
    // Navigate to personal info
    await page.goto('https://myaccount.google.com/personal-info');
    await page.waitForTimeout(4000);
    
    let content = await page.locator('body').innerText();
    
    if (content.includes('Basic info') || content.includes('Profile picture') || content.includes('Name')) {
      console.log('✅ Logged in! Clicking Photo...');
      
      await page.getByText('Photo').first().click();
      await page.waitForTimeout(2000);
      
      // Look for Add profile photo
      const addBtn = page.locator('button:has-text("Add profile photo")').first();
      if (await addBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await addBtn.click();
        await page.waitForTimeout(2000);
      }
      
      // From computer
      const fromComputer = page.getByText('From computer');
      if (await fromComputer.isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log('Uploading...');
        const [fileChooser] = await Promise.all([
          page.waitForEvent('filechooser', { timeout: 10000 }),
          fromComputer.click()
        ]);
        await fileChooser.setFiles(IMAGE_PATH);
        await page.waitForTimeout(4000);
        
        // Save
        const saveBtn = page.locator('button:has-text("Save as profile photo")').first();
        if (await saveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          await saveBtn.click();
          await page.waitForTimeout(3000);
          console.log('✅ Profile picture saved!');
        }
      }
    } else {
      console.log('❌ Not logged in. Page:', content.substring(0, 400));
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_quick.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_quick_error.png', fullPage: true });
  }

  await browser.close();
})();
