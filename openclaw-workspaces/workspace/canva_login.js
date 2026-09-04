const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('Going to Canva...');
    await page.goto('https://www.canva.com/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: '/root/.openclaw/workspace/canva_login1.png' });
    console.log('Screenshot saved: canva_login1.png');
    
    // Look for email input or "Continue with email" button
    const pageContent = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('Page content:', pageContent);
    
    // Try to find and click "Continue with email" or similar
    const emailOptionClicked = await page.evaluate(() => {
      const buttons = document.querySelectorAll('button, a, span');
      for (const btn of buttons) {
        const text = btn.textContent.toLowerCase();
        if (text.includes('email') || text.includes('log in with email') || text.includes('continue with email')) {
          btn.click();
          return 'clicked: ' + btn.textContent.trim();
        }
      }
      return 'not found';
    });
    console.log('Email option:', emailOptionClicked);
    await page.waitForTimeout(2000);
    
    // Look for email input field
    const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email"], input[placeholder*="Email"]');
    if (emailInput) {
      await emailInput.click();
      await emailInput.type('choover323@gmail.com', { delay: 50 });
      console.log('Entered email');
      await page.waitForTimeout(1000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/canva_login2.png' });
      
      // Click Continue/Submit button
      await page.evaluate(() => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
          const text = btn.textContent.toLowerCase();
          if (text.includes('continue') || text.includes('next') || text.includes('submit') || text.includes('log in')) {
            btn.click();
            return;
          }
        }
      });
      console.log('Clicked continue');
      await page.waitForTimeout(5000);
      
      await page.screenshot({ path: '/root/.openclaw/workspace/canva_login3.png' });
      
      const afterContent = await page.evaluate(() => document.body.innerText.substring(0, 2000));
      console.log('After continue:', afterContent);
    } else {
      console.log('Email input not found, checking page structure...');
      const inputs = await page.$$eval('input', els => els.map(e => ({ type: e.type, name: e.name, placeholder: e.placeholder })));
      console.log('Inputs found:', JSON.stringify(inputs));
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
