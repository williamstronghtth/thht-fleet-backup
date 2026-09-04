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
    console.log('Logged in. URL:', page.url());

    // Navigate directly to CMA page
    const cmaUrl = 'https://www.narrpr.com/link-to-details?propertyid=58383519&orgid=fldbaa-n&listingid=1222256&pmode=1&DetailsTab=6&IsLegacy=true';
    console.log('\nNavigating to CMA page...');
    await page.goto(cmaUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);
    console.log('CMA page URL:', page.url());

    let content = await page.evaluate(() => document.body.innerText.substring(0, 10000));
    console.log('\n=== CMA PAGE CONTENT ===');
    console.log(content);

    // Take a screenshot for debugging
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_cma_page.png', fullPage: false });
    console.log('\nScreenshot saved to rpr_cma_page.png');

    // Look for tabs or sections
    const tabs = await page.$$eval('[role="tab"], [class*="tab"], .nav-link, .nav-item', els => 
      els.map(e => ({ text: e.textContent.trim().substring(0, 50), visible: e.offsetParent !== null }))
    );
    console.log('\nTabs found:', JSON.stringify(tabs, null, 2));

    // Try scrolling to find comps
    await page.evaluate(() => window.scrollTo(0, 2000));
    await page.waitForTimeout(2000);
    content = await page.evaluate(() => document.body.innerText.substring(0, 10000));
    console.log('\n=== AFTER SCROLL ===');
    console.log(content);

    // Now try the Create CMA link  
    const createCmaUrl = 'https://www.narrpr.com/link-to-details?propertyid=58383519&orgid=fldbaa-n&listingid=1222256&pmode=1&DetailsTab=6&action=editc&IsLegacy=true';
    console.log('\n\nNavigating to Create CMA...');
    await page.goto(createCmaUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);
    console.log('Create CMA URL:', page.url());
    
    content = await page.evaluate(() => document.body.innerText.substring(0, 10000));
    console.log('\n=== CREATE CMA PAGE ===');
    console.log(content);

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_create_cma.png', fullPage: false });

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
