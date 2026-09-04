const nodemailer = require('nodemailer');

async function sendEmail() {
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      user: 'william@thehooverhometeam.com',
      pass: 'jvjnairgefinleph'
    }
  });

  const htmlBody = `
<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
  <h2 style="color: #1e3a5f;">☀️ Good morning, Chris!</h2>
  <p>Happy Friday! Here's your Morning Brief for February 6th, 2026.</p>
  
  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
  
  <h3 style="color: #1e3a5f;">📰 TOP REAL ESTATE NEWS</h3>
  
  <p><strong>1. National Housing Market Steady, But Regional Gaps Widen</strong><br>
  The national market closed January flat — median list price holding at $419,999, inventory at 696K homes. But the real story is regional: Northeast is hot (MAI 38.1, fastest turnover), South is most buyer-friendly (32.7% price reductions), and the West remains priciest at $616K median. Florida's in that Southern mix where buyers have leverage.</p>
  
  <p><strong>2. AI Adoption Becoming Competitive Edge for Agents</strong><br>
  Tom Ferry coach Jason Pantana told HousingWire that the gap between agents "dabbling" in AI vs. fully adopting it is becoming one of the biggest competitive divides in real estate. His advice: 15-20 min/day learning what's new. Also warned that AI can hallucinate — always fact-check.</p>
  
  <p><strong>3. Mortgage Rates Tick Up Amid Shutdown Uncertainty</strong><br>
  30-year rates rose to 6.23% this week (up from 6.18%). The January jobs report was delayed by the latest federal government shutdown. ADP showed only 22K private jobs created — weak numbers could push the Fed toward earlier rate cuts. MBA expects rates to stay in the 6-6.5% range for 2026.</p>
  
  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
  
  <h3 style="color: #1e3a5f;">📊 TODAY'S MORTGAGE RATES</h3>
  
  <table style="border-collapse: collapse; width: 100%;">
    <tr><td style="padding: 5px 10px;">30-Year Fixed:</td><td style="padding: 5px 10px;"><strong>6.26%</strong></td></tr>
    <tr><td style="padding: 5px 10px;">15-Year Fixed:</td><td style="padding: 5px 10px;"><strong>5.63%</strong></td></tr>
    <tr><td style="padding: 5px 10px;">10-Year Fixed:</td><td style="padding: 5px 10px;"><strong>5.53%</strong></td></tr>
    <tr><td style="padding: 5px 10px;">5/1 ARM:</td><td style="padding: 5px 10px;"><strong>5.44%</strong></td></tr>
    <tr><td style="padding: 5px 10px;">10-Year Treasury:</td><td style="padding: 5px 10px;"><strong>4.20%</strong></td></tr>
  </table>
  
  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
  
  <h3 style="color: #1e3a5f;">✍️ DRAFT BLOG POST</h3>
  
  <p><strong>Title:</strong> Today's Real Estate News — February 6, 2026</p>
  
  <p><strong>Housing Market Steady, But Location Matters More Than Ever</strong></p>
  
  <p>The national housing market finished January on stable footing. Median list prices held at $420K and inventory stayed flat at around 696,000 homes.</p>
  
  <p>But dig into the data and you'll see the real story: regional differences are widening. The Northeast is seeing the strongest seller conditions. The South — including Florida — remains the most buyer-friendly market in the country.</p>
  
  <p>What does that mean for you? If you're buying in Florida, you have more negotiating power than buyers in most other parts of the country. Over 32% of listings here have had price reductions — that's leverage.</p>
  
  <p>Meanwhile, mortgage rates ticked up slightly to 6.26% for a 30-year fixed. Rates are expected to stay in the 6-6.5% range through 2026, so waiting for a dramatic drop isn't a winning strategy.</p>
  
  <p>The takeaway? The market rewards those who act with good information. If you're thinking about buying or selling, let's talk about what the numbers mean for your specific situation.</p>
  
  <p>— Chris Hoover, The Hoover Home Team</p>
  
  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
  
  <p style="color: #666; font-size: 12px;">
    William Strong | The Hoover Home Team<br>
    william@thehooverhometeam.com
  </p>
</div>
`;

  const textBody = `☀️ Good morning, Chris!

Happy Friday! Here's your Morning Brief for February 6th, 2026.

---

📰 TOP REAL ESTATE NEWS

1. National Housing Market Steady, But Regional Gaps Widen
The national market closed January flat — median list price holding at $419,999, inventory at 696K homes. But the real story is regional: Northeast is hot (MAI 38.1, fastest turnover), South is most buyer-friendly (32.7% price reductions), and the West remains priciest at $616K median. Florida's in that Southern mix where buyers have leverage.

2. AI Adoption Becoming Competitive Edge for Agents
Tom Ferry coach Jason Pantana told HousingWire that the gap between agents "dabbling" in AI vs. fully adopting it is becoming one of the biggest competitive divides in real estate. His advice: 15-20 min/day learning what's new. Also warned that AI can hallucinate — always fact-check.

3. Mortgage Rates Tick Up Amid Shutdown Uncertainty
30-year rates rose to 6.23% this week (up from 6.18%). The January jobs report was delayed by the latest federal government shutdown. ADP showed only 22K private jobs created — weak numbers could push the Fed toward earlier rate cuts. MBA expects rates to stay in the 6-6.5% range for 2026.

---

📊 TODAY'S MORTGAGE RATES

• 30-Year Fixed: 6.26%
• 15-Year Fixed: 5.63%
• 10-Year Fixed: 5.53%
• 5/1 ARM: 5.44%
• 10-Year Treasury: 4.20%

---

✍️ DRAFT BLOG POST

Title: Today's Real Estate News — February 6, 2026

Housing Market Steady, But Location Matters More Than Ever

The national housing market finished January on stable footing. Median list prices held at $420K and inventory stayed flat at around 696,000 homes.

But dig into the data and you'll see the real story: regional differences are widening. The Northeast is seeing the strongest seller conditions. The South — including Florida — remains the most buyer-friendly market in the country.

What does that mean for you? If you're buying in Florida, you have more negotiating power than buyers in most other parts of the country. Over 32% of listings here have had price reductions — that's leverage.

Meanwhile, mortgage rates ticked up slightly to 6.26% for a 30-year fixed. Rates are expected to stay in the 6-6.5% range through 2026, so waiting for a dramatic drop isn't a winning strategy.

The takeaway? The market rewards those who act with good information. If you're thinking about buying or selling, let's talk about what the numbers mean for your specific situation.

— Chris Hoover, The Hoover Home Team

---

William Strong | The Hoover Home Team
william@thehooverhometeam.com`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'ch@thehooverhometeam.com',
      subject: '☀️ Morning Brief — February 6, 2026',
      text: textBody,
      html: htmlBody
    });
    
    console.log('✅ Morning brief sent!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed to send:', error.message);
  }
}

sendEmail();
