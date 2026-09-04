const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process'
    ]
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York'
  });
  
  // Remove webdriver property
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  const page = await context.newPage();

  try {
    console.log('Going to Canva...');
    await page.goto('https://www.canva.com/login', { waitUntil: 'networkidle', timeout: 60000 });
    
    // Wait for Cloudflare check
    console.log('Waiting for page to load...');
    await page.waitForTimeout(10000);
    
    await page.screenshot({ path: '/root/.openclaw/workspace/canva_cf.png' });
    
    const pageContent = await page.evaluate(() => document.body.innerText.substring(0, 2000));
    console.log('Page content:', pageContent);
    
    // Check if we passed Cloudflare
    if (pageContent.includes('Ray ID') || pageContent.includes('checking')) {
      console.log('Still on Cloudflare check, waiting more...');
      await page.waitForTimeout(10000);
      await page.screenshot({ path: '/root/.openclaw/workspace/canva_cf2.png' });
      const content2 = await page.evaluate(() => document.body.innerText.substring(0, 2000));
      console.log('After wait:', content2);
    }
    
    // Try to find login elements
    const inputs = await page.$$eval('input:visible', els => els.map(e => ({ 
      type: e.type, name: e.name, placeholder: e.placeholder, id: e.id 
    })));
    console.log('Visible inputs:', JSON.stringify(inputs));

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
