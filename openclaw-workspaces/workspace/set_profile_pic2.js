const { chromium } = require('playwright');

const IMAGE_PATH = '/root/.openclaw/media/inbound/file_3---586e4174-5037-4b57-9a64-4862ac9172f2.jpg';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    // Go directly to Gmail which forces proper login
    console.log('Going to Gmail...');
    await page.goto('https://mail.google.com');
    await page.waitForTimeout(3000);
    
    console.log('Logging in...');
    await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    await page.fill('input[type="password"]', 'WilliamStrong2026!HHT');
    await page.keyboard.press('Enter');
    
    // Wait for Gmail to fully load
    console.log('Waiting for Gmail to load...');
    await page.waitForTimeout(10000);
    
    console.log('Current URL:', page.url());
    
    // Now go to profile settings from Gmail
    console.log('Going to Google Account...');
    await page.goto('https://myaccount.google.com/personal-info');
    await page.waitForTimeout(5000);
    
    let content = await page.locator('body').innerText();
    console.log('Personal info page:', content.substring(0, 800));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_page2.png', fullPage: true });
    
    // Check if we're logged in
    if (!content.includes('Sign in')) {
      console.log('✅ Logged in! Looking for photo option...');
      
      // Find and click on Photo
      const photoOption = page.getByText('Photo').first();
      if (await photoOption.isVisible({ timeout: 5000 }).catch(() => false)) {
        await photoOption.click();
        await page.waitForTimeout(3000);
        
        content = await page.locator('body').innerText();
        console.log('After clicking Photo:', content.substring(0, 1000));
        await page.screenshot({ path: '/root/.openclaw/workspace/photo_dialog.png', fullPage: true });
      }
      
      // Look for change/add photo button
      const changeBtn = page.locator('button:has-text("Change"), button:has-text("Add profile photo")').first();
      if (await changeBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await changeBtn.click();
        await page.waitForTimeout(3000);
      }
      
      // Look for "From computer" or file upload
      const fromComputer = page.getByText('From computer');
      if (await fromComputer.isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log('Found From computer option...');
        
        const [fileChooser] = await Promise.all([
          page.waitForEvent('filechooser', { timeout: 10000 }),
          fromComputer.click()
        ]);
        
        console.log('Uploading image...');
        await fileChooser.setFiles(IMAGE_PATH);
        await page.waitForTimeout(5000);
        
        await page.screenshot({ path: '/root/.openclaw/workspace/photo_uploaded.png', fullPage: true });
        
        // Click crop/save
        const saveBtn = page.locator('button:has-text("Save as profile photo"), button:has-text("Save"), button:has-text("Done")').first();
        if (await saveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          await saveBtn.click();
          await page.waitForTimeout(3000);
        }
        
        console.log('✅ Profile picture should be updated!');
      }
    } else {
      console.log('❌ Not logged in');
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_final.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_error2.png', fullPage: true });
  }

  await browser.close();
})();
