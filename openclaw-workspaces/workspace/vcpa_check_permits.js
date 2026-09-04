const { chromium } = require('playwright');

const ALTKEYS = [
  { name: '134 Deskin Dr', altkey: '5288625' },
  { name: '806 Silk Oak Ct', altkey: '3728823' },
  { name: '1108 Loch Laggan Ct', altkey: '5155676' }
];

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  // Accept disclaimer
  await page.goto('https://vcpa.vcgov.org/parcel/summary/?altkey=5288625', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button, a');
    for (const btn of btns) {
      if (btn.textContent.trim() === 'Agree') btn.click();
    }
  });
  await page.waitForTimeout(2000);

  for (const prop of ALTKEYS) {
    console.log('\n' + '='.repeat(60));
    console.log(prop.name);
    console.log('='.repeat(60));

    // Go directly to permits page
    await page.goto(`https://vcpa.vcgov.org/parcel/permits/?altkey=${prop.altkey}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    // Get full content
    const content = await page.evaluate(() => document.body.innerText);
    
    // Look for permit table data
    if (content.includes('Date') && content.includes('Number') && content.includes('Description')) {
      // Extract just the permits section
      const startIdx = content.indexOf('Date');
      const endIdx = content.indexOf('Home\nPermits');
      if (startIdx > -1) {
        const permitSection = content.substring(startIdx, endIdx > startIdx ? endIdx : startIdx + 2000);
        console.log('\nPERMIT SECTION:');
        console.log(permitSection);
      }
    } else if (content.includes('No permits')) {
      console.log('No permits on file');
    } else {
      console.log('Permit section not found');
      console.log('Content sample:', content.substring(0, 1500));
    }
  }

  await browser.close();
})();
