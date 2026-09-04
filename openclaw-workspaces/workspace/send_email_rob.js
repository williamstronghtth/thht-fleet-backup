const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Login to Gmail
  console.log('Logging into Gmail...');
  await page.goto('https://accounts.google.com/signin/v2/identifier?service=mail');
  await page.fill('input[type="email"]', 'william@thehooverhometeam.com');
  await page.click('#identifierNext');
  await page.waitForTimeout(2000);
  
  await page.fill('input[type="password"]', 'n7J>=A8MbG*Y5mD&');
  await page.click('#passwordNext');
  await page.waitForTimeout(5000);

  // Go to Gmail compose
  console.log('Opening Gmail...');
  await page.goto('https://mail.google.com/mail/u/0/#inbox');
  await page.waitForTimeout(3000);

  // Click Compose button
  console.log('Composing email...');
  await page.click('div[gh="cm"]');
  await page.waitForTimeout(2000);

  // Fill in To field
  await page.fill('input[name="to"]', 'rob@cbccr.com');
  
  // Add CC - click the Cc link first
  await page.click('span[data-tooltip="Add Cc"]');
  await page.waitForTimeout(500);
  await page.fill('input[name="cc"]', 'ch@thehooverhometeam.com');

  // Fill subject
  await page.fill('input[name="subjectbox"]', 'Introduction from The Hoover Home Team');

  // Fill body
  const emailBody = `Hi Rob,

I wanted to reach out and introduce myself — I'm William Strong, and I work alongside Chris Hoover at The Hoover Home Team.

Chris speaks highly of his time at Coldwell Banker, and I know he values the relationships he built there. I'm reaching out to let you know we're always here if there's anything we can help with — whether it's a referral, market insights, or just connecting on a deal.

Looking forward to staying in touch!

Best,
William Strong
The Hoover Home Team
william@thehooverhometeam.com`;

  await page.fill('div[aria-label="Message Body"]', emailBody);
  await page.waitForTimeout(1000);

  // Send the email
  console.log('Sending email...');
  await page.click('div[aria-label*="Send"]');
  await page.waitForTimeout(3000);

  console.log('✅ Email sent to rob@cbccr.com (CC: ch@thehooverhometeam.com)');
  
  await browser.close();
})();
