const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Navigating to RPR login...');
    await page.goto('https://auth.narrpr.com/auth/sign-in', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Log all input fields on the page
    const inputs = await page.$$eval('input', els => els.map(e => ({
      type: e.type, name: e.name, id: e.id, placeholder: e.placeholder, 'aria-label': e.getAttribute('aria-label')
    })));
    console.log('Input fields found:', JSON.stringify(inputs, null, 2));

    // Log all buttons
    const buttons = await page.$$eval('button', els => els.map(e => ({
      text: e.textContent.trim(), type: e.type, id: e.id
    })));
    console.log('Buttons found:', JSON.stringify(buttons, null, 2));

    // Try filling by various selectors
    // Email
    await page.fill('input[type="email"]', 'ch@thehooverhometeam.com').catch(async () => {
      console.log('No email type input, trying others...');
      const allInputs = await page.$$('input:visible');
      if (allInputs.length > 0) {
        await allInputs[0].fill('ch@thehooverhometeam.com');
        console.log('Filled first visible input with email');
      }
    });

    await page.waitForTimeout(1000);

    // Password
    await page.fill('input[type="password"]', 'Football37!').catch(async () => {
      console.log('No password type input, trying others...');
      const allInputs = await page.$$('input:visible');
      if (allInputs.length > 1) {
        await allInputs[1].fill('Football37!');
        console.log('Filled second visible input with password');
      }
    });

    await page.waitForTimeout(1000);
    
    // Screenshot before clicking sign in
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_before_login.png' });
    console.log('Pre-login screenshot saved');

    // Click Sign In button
    await page.click('button:has-text("Sign In")').catch(async () => {
      console.log('Could not find Sign In button by text, trying submit...');
      await page.click('button[type="submit"]').catch(() => {
        console.log('No submit button either');
      });
    });

    console.log('Clicked sign in, waiting for navigation...');
    await page.waitForURL('**/narrpr.com/**', { timeout: 15000 }).catch(() => {
      console.log('Did not navigate to narrpr.com');
    });
    
    await page.waitForTimeout(5000);
    console.log('Final URL:', page.url());
    console.log('Final title:', await page.title());

    // Check for error messages
    const errorText = await page.$$eval('[class*="error"], [class*="alert"], [role="alert"]', els => els.map(e => e.textContent.trim()));
    if (errorText.length) console.log('Error messages:', errorText);

    const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 1500));
    console.log('Page content:', bodyText);

    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_after_login.png' });
    console.log('Post-login screenshot saved');

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
