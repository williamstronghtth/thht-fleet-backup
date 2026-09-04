const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: 'smtp.gmail.com',
  port: 587,
  secure: false,
  auth: {
    user: 'william@thehooverhometeam.com',
    pass: 'jvjnairgefinleph'
  }
});

const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; }
    h1 { color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; }
    h2 { color: #2c5282; margin-top: 30px; border-left: 4px solid #3182ce; padding-left: 12px; }
    h3 { color: #2d3748; margin-top: 20px; }
    .highlight { background: #ebf8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3182ce; }
    .rate-box { background: #f0fff4; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
    .rate-number { font-size: 36px; font-weight: bold; color: #276749; }
    .rate-label { color: #718096; font-size: 14px; }
    .local-news { background: #fffaf0; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ed8936; }
    .nh-news { background: #faf5ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #805ad5; }
    .blog-idea { background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px dashed #a0aec0; }
    .skills-section { background: #e6fffa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #38b2ac; }
    ul { padding-left: 20px; }
    li { margin: 8px 0; }
    a { color: #3182ce; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 14px; }
    .emoji { font-size: 1.2em; }
  </style>
</head>
<body>
  <h1>☀️ Morning Brief — Tuesday, March 31, 2026</h1>
  
  <h2>📊 National Real Estate News</h2>
  <div class="highlight">
    <strong>Key Headlines:</strong>
    <ul>
      <li><strong>Senate Passes Major Housing Bill</strong> — Bipartisan legislation passed March 13 aims to increase supply, curb institutional investors, and address affordability crisis</li>
      <li><strong>Existing Home Sales Unexpectedly Rise</strong> — February sales up, fueled by lower rates earlier in the month and slower price growth</li>
      <li><strong>Inventory Growing</strong> — Market tilting toward buyers in some regions with more price cuts and longer days on market</li>
      <li><strong>Price Growth Slowing</strong> — Forecasts predict 0-2% growth for 2026, down from previous years</li>
      <li><strong>Affordability Improving</strong> — Zillow notes $30,000+ improvement YoY due to wage gains</li>
    </ul>
  </div>

  <h2>💰 Mortgage Rates</h2>
  <div class="rate-box">
    <div class="rate-number">6.56%</div>
    <div class="rate-label">30-Year Fixed (as of March 30)</div>
  </div>
  <p><strong>Context:</strong> Rates climbed sharply this month, up from under 6% just four weeks ago. The Iran situation and inflation concerns pushed rates to their highest since September 2025. Bond markets remain volatile with ongoing geopolitical developments.</p>
  <p><em>Source: Mortgage News Daily, WSJ</em></p>

  <h2>📍 Volusia County Local News</h2>
  
  <div class="local-news">
    <h3>🏘️ Tomoka Oaks Golf Course Approved for 254 Homes</h3>
    <p><strong>Ormond Beach</strong> — City Commission approved (3-2 vote) the controversial redevelopment of the former Tomoka Oaks Golf Course for 254 single-family homes on March 25. Nearly three hours of public comment addressed traffic, safety, and neighborhood character concerns.</p>
    <p><em>Talking point: "Big changes coming to Ormond — this adds significant inventory to the market."</em></p>
  </div>

  <div class="local-news">
    <h3>🏗️ Ormond Crossings Breaks Ground</h3>
    <p><strong>Ormond Beach</strong> — After 25 years of planning, this massive 3,000-acre mixed-use project broke ground in January. Final approvals are in for up to 2,950 residential units, 200,000 sq ft retail, 900,000 sq ft office, and 800,000 sq ft industrial space. This will transform North Ormond Beach.</p>
  </div>

  <div class="local-news">
    <h3>🏢 Northshore District Gets First Approval</h3>
    <p><strong>Daytona Beach</strong> — Commission unanimously approved first reading (March 10) for a 175.6-acre mixed-use district west of the city. Capacity: 773 residential units, 800,000 sq ft industrial, 826,000 sq ft commercial. 40% preserved natural areas. Final vote May 20.</p>
  </div>

  <h2>🌲 Southern New Hampshire News</h2>
  
  <div class="nh-news">
    <h3>🏠 Doucet Landing — New Development in South Nashua</h3>
    <p><strong>Nashua</strong> — 83 detached condominiums under construction in desirable South Nashua by Beote Construction. Ranch and colonial styles with Energy Star features and high-end finishes. Affordable units and model homes now available.</p>
    <p><em>Good to know for NH referrals!</em></p>
  </div>

  <div class="nh-news">
    <h3>📈 Nashua Named "Housing Champion"</h3>
    <p><strong>Nashua</strong> — The city issued 159 building permits in 2024, contributing to 5,800+ units potentially added statewide in 2025. Q1 2026 market remains resilient with limited inventory driving demand. Mayor's 2026 State of Nashua address highlighted housing as a continued challenge.</p>
  </div>

  <h2>📝 Blog Post Idea</h2>
  <div class="blog-idea">
    <h3>"Ormond Beach is Changing: What the Tomoka Oaks and Ormond Crossings Approvals Mean for Homeowners"</h3>
    <p><strong>Angle:</strong> Local-focused piece explaining how 3,000+ new housing units coming to Ormond Beach over the next few years will affect current homeowners and buyers.</p>
    <p><strong>Key Points:</strong></p>
    <ul>
      <li>Tomoka Oaks: 254 homes on former golf course — what this means for nearby property values</li>
      <li>Ormond Crossings: 2,950 units + commercial = new job centers and amenities</li>
      <li>How increased inventory might affect sellers thinking of listing in 2026-2027</li>
      <li>Opportunity for buyers: more options coming, but the best existing homes will still move fast</li>
    </ul>
    <p><strong>CTA:</strong> "Thinking about selling before new inventory hits? Let's talk about timing your sale for maximum value."</p>
  </div>

  <h2>📅 Today's Calendar</h2>
  <p><em>Calendar check not available — please review your Google Calendar for today's appointments.</em></p>

  <h2>📚 Skills Learned Since Last Brief</h2>
  <div class="skills-section">
    <p>From <code>memory/skills-learning.md</code> — here's what we've been building:</p>
    
    <h3>1. Prospecting Email Templates (3/19)</h3>
    <p>Built 6 ready-to-use templates: expired listings, FSBO, just listed/sold nearby, sphere check-ins, open house follow-ups, circle prospecting. Saved to <code>templates/prospecting-emails.md</code>.</p>
    
    <h3>2. Market Data Pipeline (3/19)</h3>
    <p>Created <code>scripts/market-snapshot.py</code> — pulls Redfin's free public data, filters for Florida metros, generates formatted snapshots with YoY trends. Key finding: Cape Coral prices down 4.9% but sales up 29% (buyer's market).</p>
    
    <h3>3. Objection Handling Scripts (3/19)</h3>
    <p>Built <code>templates/objection-handling-scripts.md</code> with 8 complete scripts covering common seller objections (not interested, have agent, waiting, FSBO, commission, etc.). Plus roleplay scenarios in <code>templates/cold-call-roleplay-practice.md</code>.</p>
    
    <p><strong>Together these form a complete prospecting workflow:</strong> Pull market data → Call with scripts → Follow up with email templates.</p>
  </div>

  <div class="footer">
    <p>Generated by William Strong | The Hoover Home Team<br>
    <em>Have a great day, Chris! 🚀</em></p>
  </div>
</body>
</html>
`;

async function sendEmail() {
  try {
    const info = await transporter.sendMail({
      from: '"William Strong" <william@thehooverhometeam.com>',
      to: 'ch@thehooverhometeam.com',
      subject: '☀️ Morning Brief — Tuesday, March 31, 2026',
      html: htmlContent
    });
    console.log('Email sent successfully!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('Error sending email:', error);
  }
}

sendEmail();
