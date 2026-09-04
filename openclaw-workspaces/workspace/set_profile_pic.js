const { chromium } = require('playwright');
const path = require('path');

const IMAGE_PATH = '/root/.openclaw/media/inbound/file_3---586e4174-5037-4b57-9a64-4862ac9172f2.jpg';

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
    
    console.log('Navigating to profile picture settings...');
    await page.goto('https://myaccount.google.com/personal-info');
    await page.waitForTimeout(3000);
    
    // Click on the profile photo section
    console.log('Looking for profile photo option...');
    const photoLink = page.locator('a[href*="profile-photo"], [data-photo-action]').first();
    
    // Try clicking on "Photo" or the profile image area
    const photoSection = page.getByText('Photo').first();
    if (await photoSection.isVisible({ timeout: 5000 }).catch(() => false)) {
      await photoSection.click();
      await page.waitForTimeout(3000);
    } else {
      // Try direct URL
      await page.goto('https://myaccount.google.com/profile-photo');
      await page.waitForTimeout(3000);
    }
    
    let content = await page.locator('body').innerText();
    console.log('Current page:', content.substring(0, 1000));
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_page.png', fullPage: true });
    
    // Look for "Add profile photo" or "Change" button
    const addPhotoBtn = page.locator('button:has-text("Add"), button:has-text("Change"), [aria-label*="photo"]').first();
    if (await addPhotoBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      console.log('Found photo button, clicking...');
      await addPhotoBtn.click();
      await page.waitForTimeout(3000);
      
      content = await page.locator('body').innerText();
      console.log('After click:', content.substring(0, 1000));
      await page.screenshot({ path: '/root/.openclaw/workspace/profile_upload.png', fullPage: true });
    }
    
    // Look for file input or "From computer" option
    const fromComputer = page.getByText('From computer');
    if (await fromComputer.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('Clicking From computer...');
      
      // Set up file chooser before clicking
      const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser'),
        fromComputer.click()
      ]);
      
      console.log('Uploading image...');
      await fileChooser.setFiles(IMAGE_PATH);
      await page.waitForTimeout(5000);
      
      // Look for Save/Done button
      const saveBtn = page.locator('button:has-text("Save"), button:has-text("Done")').first();
      if (await saveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        await saveBtn.click();
        await page.waitForTimeout(3000);
      }
      
      console.log('✅ Profile picture uploaded!');
    } else {
      // Try finding file input directly
      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        console.log('Found file input, uploading...');
        await fileInput.setInputFiles(IMAGE_PATH);
        await page.waitForTimeout(5000);
        console.log('✅ File uploaded via input!');
      }
    }
    
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_result.png', fullPage: true });
    
    content = await page.locator('body').innerText();
    console.log('\nFinal page state:', content.substring(0, 800));
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/profile_error.png', fullPage: true });
  }

  await browser.close();
})();
