const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    console.log('Navigating to RPR...');
    await page.goto('https://www.narrpr.com/', { timeout: 60000 });
    await page.waitForTimeout(3000);
    
    // Look for login
    console.log('Looking for login...');
    const pageContent = await page.content();
    
    if (pageContent.includes('Sign In') || pageContent.includes('Login')) {
      console.log('Need to login...');
      
      // Try to find and click sign in
      try {
        await page.click('text=Sign In', { timeout: 5000 });
      } catch (e) {
        await page.click('text=Login', { timeout: 5000 }).catch(() => {});
      }
      
      await page.waitForTimeout(2000);
      
      // Fill login form
      await page.fill('input[type="email"], input[name="email"], #email', 'ch@thehooverhometeam.com').catch(() => {});
      await page.fill('input[type="password"], input[name="password"], #password', 'Football37!').catch(() => {});
      
      // Submit
      await page.click('button[type="submit"], input[type="submit"]').catch(() => {});
      await page.waitForTimeout(5000);
    }
    
    // Search for property
    console.log('Searching for 6085 Sanctuary Garden Blvd...');
    
    // Find search input
    const searchSelectors = ['input[placeholder*="Search"]', 'input[type="search"]', '#search', '.search-input'];
    for (const sel of searchSelectors) {
      try {
        await page.fill(sel, '6085 Sanctuary Garden Blvd, Port Orange, FL');
        await page.keyboard.press('Enter');
        console.log('Search submitted via:', sel);
        break;
      } catch (e) {}
    }
    
    await page.waitForTimeout(8000);
    
    // Screenshot
    await page.screenshot({ path: '/tmp/rpr_result.png', fullPage: true });
    console.log('Screenshot saved');
    
    // Get text content
    const text = await page.innerText('body').catch(() => 'Could not get text');
    console.log('Page text (first 2000 chars):', text.substring(0, 2000));
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/tmp/rpr_error.png' }).catch(() => {});
  } finally {
    await browser.close();
  }
})();
