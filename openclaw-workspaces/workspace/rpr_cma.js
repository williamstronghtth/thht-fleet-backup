const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox', '--disable-dev-shm-usage'] 
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    // Login to RPR
    console.log('🔐 Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('✅ Logged in.');

    // Go directly to property page
    console.log('📍 Loading property page...');
    await page.goto('https://www.narrpr.com/properties/details/info/56429173', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);
    
    // Click on CMA tab
    console.log('📊 Opening CMA tab...');
    await page.click('text=CMA');
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: '/tmp/rpr_cma.png', fullPage: false });
    console.log('📸 CMA screenshot saved');
    
    // Get page content
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('\n=== CMA PAGE CONTENT ===\n');
    
    // Print lines with comp info
    const lines = bodyText.split('\n').filter(l => l.trim());
    let printCount = 0;
    for (const line of lines) {
      if (line.match(/sabal|sold|closed|\$\d|bed|bath|sqft|sq ft|price|days|dom|circle|cir|point|lake/i)) {
        console.log(line);
        printCount++;
        if (printCount > 60) break;
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/rpr_error.png' });
  } finally {
    await browser.close();
  }
})();
