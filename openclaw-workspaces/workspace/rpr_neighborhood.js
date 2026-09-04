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

    // Search for Sabal Lakes subdivision
    console.log('🔍 Searching Sabal Lakes...');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const locationInput = await page.$('input[placeholder*="Enter Address"]');
    if (locationInput) {
      await locationInput.fill('Sabal Lakes, Port Orange, FL');
      await page.waitForTimeout(2000);
      await page.keyboard.press('ArrowDown');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(5000);
    }
    
    // Try to change status to "Sold"
    console.log('📊 Filtering for sold properties...');
    const statusDropdown = await page.$('[aria-label*="Status"]') || await page.$('button:has-text("Status")') || await page.$('.status-filter');
    
    await page.screenshot({ path: '/tmp/rpr_sabal.png', fullPage: false });
    console.log('📸 Screenshot saved');
    console.log('Current URL:', page.url());
    
    // Get page text
    const bodyText = await page.evaluate(() => document.body.innerText);
    const lines = bodyText.split('\n').filter(l => l.trim());
    
    console.log('\n=== PAGE CONTENT (property-related) ===\n');
    let count = 0;
    for (const line of lines) {
      if (line.match(/sabal|\$\d|bed|bath|sqft|sold|active|pending|price|list|dom/i) && line.length < 200) {
        console.log(line);
        count++;
        if (count > 50) break;
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();
