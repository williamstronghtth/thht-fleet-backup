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
    // Login
    console.log('🔐 Logging into RPR...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    await page.fill('#SignInEmail', 'ch@thehooverhometeam.com');
    await page.fill('#SignInPassword', 'Football37!');
    await page.click('#SignInBtn');
    await page.waitForTimeout(8000);
    console.log('✅ Logged in.');

    // Go to home and search with sold filter
    console.log('🔍 Searching Sabal Point Circle with sold properties...');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Click on Type/Status dropdown to change to Public Records (includes sold)
    console.log('📊 Setting filter to Public Records...');
    const statusButton = await page.$('button:has-text("Public Reco")') || await page.$('.type-status-dropdown');
    if (statusButton) {
      await statusButton.click();
      await page.waitForTimeout(1000);
    }
    
    // Take screenshot of filter options
    await page.screenshot({ path: '/tmp/rpr_filters.png', fullPage: false });
    
    // Search for the street
    const locationInput = await page.$('input[placeholder*="Enter Address"]');
    if (locationInput) {
      await locationInput.fill('Sabal Point Circle, Port Orange, FL');
      await page.waitForTimeout(2000);
      await page.keyboard.press('ArrowDown');
      await page.waitForTimeout(500);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(6000);
    }
    
    await page.screenshot({ path: '/tmp/rpr_results.png', fullPage: false });
    console.log('📸 Screenshots saved');
    console.log('URL:', page.url());
    
    // Get property list from page
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('\n=== SEARCH RESULTS ===\n');
    console.log(bodyText.substring(0, 3000));
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();
