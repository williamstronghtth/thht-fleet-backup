const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  try {
    const setupUrl = 'https://accounts.google.com/RP?c=CPqvpaOhkrO74QEQsNGWrt2QrJUu&uc=ac&hl=en&continue=https://workspace.google.com/dashboard&fc=1&flowName=GlifWebSignIn';
    
    console.log('Navigating to setup URL...');
    await page.goto(setupUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    console.log('Page URL:', page.url());
    
    // Screenshot to see what we're dealing with
    await page.screenshot({ path: '/root/.openclaw/workspace/workspace_setup1.png', fullPage: false });
    
    // Get page content
    const content = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    console.log('\n=== PAGE CONTENT ===');
    console.log(content);

    // Look for password field or other inputs
    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type,
      name: e.name,
      id: e.id,
      placeholder: e.placeholder,
      ariaLabel: e.getAttribute('aria-label')
    })));
    console.log('\nInputs found:', JSON.stringify(inputs, null, 2));

    // Look for buttons
    const buttons = await page.$$eval('button', els => els.map(e => e.textContent.trim().substring(0, 50)));
    console.log('\nButtons:', buttons);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
