const { chromium } = require('playwright');

const ADDRESSES = [
  '134 Deskin Dr, South Daytona, FL 32119',
  '785 Falcon Dr, Port Orange, FL 32127',
  '806 Silk Oak Ct, New Smyrna Beach, FL 32168',
  '1108 Loch Laggan Ct, New Smyrna Beach, FL 32168'
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Go to RPR login
    console.log('Navigating to RPR...');
    await page.goto('https://www.narrpr.com/home', { waitUntil: 'networkidle', timeout: 30000 });

    // Fill email
    const emailField = await page.$('input[type="email"], input[name="email"], input[id*="email"], input[placeholder*="Email"]');
    if (emailField) {
      await emailField.fill('ch@thehooverhometeam.com');
      console.log('Email entered');
    }

    // Fill password
    const passField = await page.$('input[type="password"]');
    if (passField) {
      await passField.fill('Football37!');
      console.log('Password entered');
    }

    // Click sign in
    const signInBtn = await page.$('button:has-text("Sign In"), input[type="submit"]');
    if (signInBtn) {
      await signInBtn.click();
      console.log('Clicked Sign In, waiting...');
      await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
      console.log('After login URL:', page.url());
      console.log('After login title:', await page.title());
    }

    // Check if logged in
    const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Page after login:', bodyText);

    // If logged in, search each property
    for (const addr of ADDRESSES) {
      console.log(`\n--- Searching: ${addr} ---`);
      
      // Navigate to search or use search bar
      await page.goto('https://www.narrpr.com/', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      
      // Look for search field
      const searchField = await page.$('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"], input[placeholder*="address"], input[id*="search"]');
      if (searchField) {
        await searchField.fill('');
        await searchField.fill(addr);
        console.log('Address entered in search');
        
        // Press enter or click search button
        await page.keyboard.press('Enter');
        await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
        
        console.log('Search result URL:', page.url());
        
        // Wait for results and grab text
        await page.waitForTimeout(3000);
        const resultText = await page.evaluate(() => document.body.innerText.substring(0, 3000));
        console.log('Result:', resultText);
      } else {
        console.log('No search field found');
        const currentText = await page.evaluate(() => document.body.innerText.substring(0, 1000));
        console.log('Current page:', currentText);
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
