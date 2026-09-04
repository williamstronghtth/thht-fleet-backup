const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Login
    console.log('Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('Logged in.');

    // Go to CMA page
    const cmaUrl = 'https://www.narrpr.com/homes/fl/new-smyrna-beach/32168/1108-loch-laggan-ct/58383519-valuation.aspx?orgid=fldbaa-n&listingid=1222256&pmode=1';
    await page.goto(cmaUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);
    console.log('On CMA page.');

    // Step 1: Click "Confirm Facts" 
    console.log('\n--- Step 1: Confirm Home Facts ---');
    await page.click('text=Confirm Facts');
    await page.waitForTimeout(5000);
    console.log('Confirm Facts dialog open.');

    // Find ALL clickable elements in the dialog
    const allClickables = await page.evaluate(() => {
      const dialog = document.querySelector('.ui-dialog');
      if (!dialog) return ['No dialog found'];
      const els = dialog.querySelectorAll('a, button, input[type="button"], input[type="submit"], [onclick], [role="button"]');
      return Array.from(els).map(e => ({
        tag: e.tagName,
        text: e.textContent.trim().substring(0, 60),
        id: e.id,
        class: e.className.toString().substring(0, 80),
        href: e.href || '',
        type: e.type || '',
        visible: e.offsetWidth > 0 && e.offsetHeight > 0
      }));
    });
    console.log('Dialog clickables:', JSON.stringify(allClickables, null, 2));

    // Try to click "Confirm Facts and Close" using various methods
    // Method 1: Find it as a link/button within the dialog
    let clicked = false;
    
    // Try clicking by text content
    try {
      await page.click('.ui-dialog >> text=Confirm Facts and Close', { timeout: 5000 });
      clicked = true;
      console.log('Clicked via text selector');
    } catch(e) {
      console.log('Text selector failed, trying alternatives...');
    }

    if (!clicked) {
      // Method 2: JavaScript click
      const result = await page.evaluate(() => {
        const dialog = document.querySelector('.ui-dialog');
        if (!dialog) return 'No dialog';
        const allEls = dialog.querySelectorAll('*');
        for (const el of allEls) {
          if (el.textContent.trim() === 'Confirm Facts and Close') {
            el.click();
            return 'Clicked: ' + el.tagName + '.' + el.className;
          }
        }
        // Also try partial match
        for (const el of allEls) {
          if (el.textContent.includes('Confirm Facts and Close') && el.children.length === 0) {
            el.click();
            return 'Clicked partial: ' + el.tagName + '.' + el.className;
          }
        }
        return 'Not found';
      });
      console.log('JS click result:', result);
      if (result.startsWith('Clicked')) clicked = true;
    }

    await page.waitForTimeout(5000);
    
    // Check if overlay is gone
    const overlayPresent = await page.evaluate(() => {
      const overlay = document.querySelector('.ui-widget-overlay');
      return overlay && overlay.offsetWidth > 0;
    });
    console.log('Overlay still present:', overlayPresent);

    if (overlayPresent) {
      // Try pressing Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(2000);
      const stillPresent = await page.evaluate(() => {
        const overlay = document.querySelector('.ui-widget-overlay');
        return overlay && overlay.offsetWidth > 0;
      });
      console.log('After Escape, overlay present:', stillPresent);
    }

    // Step 2: Find Comps
    console.log('\n--- Step 2: Find Comps ---');
    try {
      await page.click('text=Find Comps', { timeout: 10000 });
      await page.waitForTimeout(10000);
      console.log('Clicked Find Comps!');
      console.log('URL:', page.url());
      
      let content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n=== COMPS PAGE ===');
      console.log(content);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_results.png', fullPage: false });
    } catch(e) {
      console.log('Find Comps click failed:', e.message.substring(0, 200));
      
      // Force click via JS
      const jsResult = await page.evaluate(() => {
        const els = document.querySelectorAll('a, button, [onclick]');
        for (const el of els) {
          if (el.textContent.trim().includes('Find Comps')) {
            el.click();
            return 'Force clicked: ' + el.tagName;
          }
        }
        return 'Not found';
      });
      console.log('JS force click:', jsResult);
      await page.waitForTimeout(10000);
      
      let content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
      console.log('\n=== COMPS PAGE (after force click) ===');
      console.log(content);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_results.png', fullPage: false });
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
