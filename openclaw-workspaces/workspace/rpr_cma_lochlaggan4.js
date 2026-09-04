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
    console.log('Logged in.');

    // Go to CMA page
    const cmaUrl = 'https://www.narrpr.com/homes/fl/new-smyrna-beach/32168/1108-loch-laggan-ct/58383519-valuation.aspx?orgid=fldbaa-n&listingid=1222256&pmode=1';
    await page.goto(cmaUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(8000);
    console.log('On CMA page.');

    // Step 1: Click "Confirm Facts"
    console.log('\n--- Step 1: Confirm Home Facts ---');
    const confirmBtn = await page.$('text=Confirm Facts');
    if (confirmBtn) {
      await confirmBtn.click();
      await page.waitForTimeout(5000);
      console.log('Clicked Confirm Facts');
      
      // Screenshot to see the modal
      await page.screenshot({ path: '/root/.openclaw/workspace/rpr_confirm_facts.png', fullPage: false });
      
      // Check what's in the modal/dialog
      const dialogContent = await page.evaluate(() => {
        const dialog = document.querySelector('.ui-dialog, [role="dialog"], .modal');
        if (dialog) return dialog.innerText.substring(0, 3000);
        // Also check for any overlay content
        const overlay = document.querySelector('.ui-dialog-content, .modal-content, .dialog-content');
        if (overlay) return overlay.innerText.substring(0, 3000);
        return 'No dialog found';
      });
      console.log('Dialog content:', dialogContent);

      // Look for all visible buttons
      const buttons = await page.$$eval('button:visible, input[type="button"]:visible, input[type="submit"]:visible, a.btn:visible, .ui-dialog button', 
        els => els.map(e => ({ text: e.textContent.trim().substring(0, 50), visible: e.offsetParent !== null, tag: e.tagName, class: e.className.substring(0, 80) }))
      );
      console.log('Visible buttons:', JSON.stringify(buttons, null, 2));

      // Try to find and click a save/confirm/close button in the dialog
      const dialogBtns = await page.$$('.ui-dialog button, [role="dialog"] button, .modal button');
      console.log(`Found ${dialogBtns.length} dialog buttons`);
      
      for (const btn of dialogBtns) {
        const text = await btn.textContent();
        console.log('  Dialog button:', text.trim());
      }

      // Try clicking the confirm/save button within dialog
      const saveInDialog = await page.$('.ui-dialog button:has-text("Save"), .ui-dialog button:has-text("Confirm"), .ui-dialog button:has-text("OK"), .ui-dialog button:has-text("Done"), .ui-dialog button:has-text("Continue"), .ui-dialog button:has-text("Close")');
      if (saveInDialog) {
        const btnText = await saveInDialog.textContent();
        console.log('Clicking dialog button:', btnText.trim());
        await saveInDialog.click();
        await page.waitForTimeout(3000);
      } else {
        // Try clicking any button with class containing "confirm" or "save"
        const confirmInPage = await page.$('button[class*="confirm"], button[class*="save"], .btn-primary, .ui-button');
        if (confirmInPage) {
          const btnText = await confirmInPage.textContent();
          console.log('Clicking fallback button:', btnText.trim());
          await confirmInPage.click();
          await page.waitForTimeout(3000);
        }
      }
      
      // Check if overlay is gone
      const overlayGone = await page.evaluate(() => {
        const overlay = document.querySelector('.ui-widget-overlay');
        return !overlay || overlay.style.display === 'none';
      });
      console.log('Overlay gone:', overlayGone);

      // Full page content after dialog interaction
      const content = await page.evaluate(() => document.body.innerText.substring(0, 8000));
      console.log('\n=== PAGE AFTER DIALOG ===');
      console.log(content);
    }

    // Screenshot final state
    await page.screenshot({ path: '/root/.openclaw/workspace/rpr_after_confirm.png', fullPage: false });

    // Now try Find Comps
    console.log('\n--- Step 2: Find Comps ---');
    const findCompsBtn = await page.$('text=Find Comps');
    if (findCompsBtn) {
      const isVisible = await findCompsBtn.isVisible();
      console.log('Find Comps visible:', isVisible);
      if (isVisible) {
        await findCompsBtn.click({ force: true });
        await page.waitForTimeout(10000);
        console.log('Clicked Find Comps');
        console.log('URL:', page.url());
        
        const content = await page.evaluate(() => document.body.innerText.substring(0, 15000));
        console.log('\n=== COMPS PAGE ===');
        console.log(content);
        
        await page.screenshot({ path: '/root/.openclaw/workspace/rpr_comps_results.png', fullPage: false });
      }
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
