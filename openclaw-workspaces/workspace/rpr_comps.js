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

    // Go to home page
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Use the Location search box
    console.log('🔍 Searching for subject property...');
    const locationInput = await page.$('input[placeholder*="Enter Address"]');
    if (locationInput) {
      await locationInput.click();
      await locationInput.fill('6110 Sabal Point Circle, Port Orange, FL');
      await page.waitForTimeout(2000);
      
      // Wait for autocomplete and click first result
      await page.keyboard.press('ArrowDown');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(5000);
      console.log('📍 Property selected. URL:', page.url());
    }
    
    await page.screenshot({ path: '/tmp/rpr_property.png', fullPage: false });
    console.log('📸 Screenshot saved');
    
    // Try to get property details from page
    const pageContent = await page.content();
    
    // Look for key data
    if (pageContent.includes('Bed') || pageContent.includes('Bath')) {
      console.log('✅ Property details page loaded');
    }
    
    // Get visible text with property info
    const bodyText = await page.evaluate(() => document.body.innerText);
    const lines = bodyText.split('\n').filter(l => l.trim());
    
    // Print relevant lines (beds, baths, sqft, etc)
    for (const line of lines.slice(0, 100)) {
      if (line.match(/bed|bath|sqft|sq ft|year|built|price|\$|acres?|lot/i)) {
        console.log(line);
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/rpr_error.png' });
  } finally {
    await browser.close();
  }
})();
