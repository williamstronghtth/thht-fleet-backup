const { chromium } = require('playwright');

const VIDEO_URL = 'https://www.youtube.com/watch?v=2a9Lx9J8uSs';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('Going to YouTube video...');
    await page.goto(VIDEO_URL);
    await page.waitForTimeout(5000);
    
    // Get video title
    const title = await page.locator('h1.ytd-video-primary-info-renderer, h1.style-scope.ytd-watch-metadata').first().textContent().catch(() => 'Unknown');
    console.log('\nVideo Title:', title.trim());
    
    // Try to get description
    const description = await page.locator('#description-text, #description').first().textContent().catch(() => 'No description');
    console.log('\nDescription:', description.substring(0, 500));
    
    // Take screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/videos/youtube_video.png', fullPage: false });
    console.log('\nScreenshot saved');
    
    // Try clicking on "...more" to expand description
    const moreBtn = page.locator('tp-yt-paper-button#expand');
    if (await moreBtn.isVisible().catch(() => false)) {
      await moreBtn.click();
      await page.waitForTimeout(1000);
      const fullDesc = await page.locator('#description-text').textContent().catch(() => '');
      console.log('\nFull Description:', fullDesc.substring(0, 1000));
    }
    
    // Check if there's a transcript button
    console.log('\nLooking for transcript option...');
    
    // Click the three dots menu under the video
    const menuBtn = page.locator('button[aria-label="More actions"]').first();
    if (await menuBtn.isVisible().catch(() => false)) {
      await menuBtn.click();
      await page.waitForTimeout(1000);
      
      // Look for "Show transcript" option
      const transcriptBtn = page.locator('text=Show transcript');
      if (await transcriptBtn.isVisible().catch(() => false)) {
        await transcriptBtn.click();
        await page.waitForTimeout(2000);
        
        // Get transcript text
        const transcriptItems = await page.locator('ytd-transcript-segment-renderer').allTextContents();
        console.log('\n=== TRANSCRIPT ===');
        console.log(transcriptItems.join('\n'));
        console.log('=== END ===');
      }
    }
    
    // Get page content as fallback
    const pageText = await page.locator('body').innerText();
    console.log('\nPage snippet:', pageText.substring(0, 800));
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/videos/youtube_error.png', fullPage: true });
  }

  await browser.close();
})();
