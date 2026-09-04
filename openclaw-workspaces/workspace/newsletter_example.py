import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = "williamstrongthht@gmail.com"
APP_PASSWORD = "yeeg jjkb smfw hxwk"

# Newsletter content
subject = "Your Weekly Real Estate Update — February 4, 2026"

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background-color: #ffffff;
  }
  .header {
    text-align: center;
    padding-bottom: 15px;
    border-bottom: 2px solid #1a3c5e;
    margin-bottom: 25px;
  }
  .header h2 {
    color: #1a3c5e;
    font-size: 22px;
    margin: 0 0 5px 0;
    font-family: Arial, Helvetica, sans-serif;
  }
  .header .subtitle {
    color: #888;
    font-size: 13px;
    font-family: Arial, Helvetica, sans-serif;
  }
  .personal-note {
    background-color: #f9f9f9;
    padding: 15px 20px;
    border-left: 3px solid #1a3c5e;
    margin-bottom: 25px;
    border-radius: 0 4px 4px 0;
  }
  .section-title {
    color: #1a3c5e;
    font-size: 18px;
    font-family: Arial, Helvetica, sans-serif;
    margin-top: 30px;
    margin-bottom: 10px;
  }
  .rates-box {
    background-color: #f4f7fa;
    padding: 15px 20px;
    border-radius: 6px;
    margin: 15px 0;
  }
  .rate-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #e0e0e0;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 15px;
  }
  .rate-row:last-child {
    border-bottom: none;
  }
  .rate-label {
    color: #555;
  }
  .rate-value {
    font-weight: bold;
    color: #1a3c5e;
  }
  .yoy {
    color: #2e7d32;
    font-size: 13px;
  }
  .cta {
    text-align: center;
    margin: 30px 0;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 6px;
  }
  .cta p {
    margin: 0;
    font-size: 16px;
  }
  .footer {
    margin-top: 30px;
    padding-top: 15px;
    border-top: 1px solid #ddd;
    font-size: 13px;
    color: #888;
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
  }
  .footer a {
    color: #1a3c5e;
    text-decoration: none;
  }
  a {
    color: #1a3c5e;
  }
</style>
</head>
<body>

<div class="header">
  <h2>The Hoover Home Team</h2>
  <div class="subtitle">Weekly Real Estate Update &bull; February 4, 2026</div>
</div>

<p>Hey there,</p>

<div class="personal-note">
We're already a month into 2026 and the market is starting to pick up steam. I've been out showing properties this week and seeing more buyers getting off the sidelines — which is a great sign. If you've been thinking about making a move, the window is open right now before spring competition heats up.
</div>

<h3 class="section-title">📊 This Week's Mortgage Rates</h3>

<div class="rates-box">
  <div class="rate-row">
    <span class="rate-label">30-Year Fixed</span>
    <span class="rate-value">6.20% <span class="yoy">↓ 0.85% YoY</span></span>
  </div>
  <div class="rate-row">
    <span class="rate-label">15-Year Fixed</span>
    <span class="rate-value">5.76% <span class="yoy">↓ 0.69% YoY</span></span>
  </div>
  <div class="rate-row">
    <span class="rate-label">30-Year Jumbo</span>
    <span class="rate-value">6.36% <span class="yoy">↓ 0.98% YoY</span></span>
  </div>
</div>

<p>Rates have been holding steady in a tight range this past couple of weeks. The big story? <strong>They're nearly a full point lower than this time last year.</strong> That's real money — on a $400K home, that's roughly $200/month less compared to a year ago. If you were priced out before, it's worth running the numbers again.</p>

<h3 class="section-title">🏡 Market Insight</h3>

<p>Inventory is still tight here in Volusia County, but we're seeing a few more listings pop up as sellers gear up for the spring market. Homes that are priced right and show well are still moving fast — especially in the $300K-$500K range.</p>

<p>For sellers: buyers are out there, and they're motivated. If you've been sitting on the fence about listing, early spring is historically one of the best times to hit the market before inventory floods in.</p>

<p>For buyers: don't wait for rates to be "perfect." A rate in the low 6s is solid by historical standards, and you can always refinance down the road if they drop further.</p>

<div class="cta">
  <p><strong>Thinking about buying or selling?</strong></p>
  <p style="margin-top: 8px;">I'd love to chat — even if you're just exploring your options. No pressure, just a conversation. Hit reply or give me a call anytime.</p>
</div>

<p>Talk soon,<br>
<strong>Chris Hoover</strong><br>
The Hoover Home Team<br>
<a href="https://thehooverhometeam.com">thehooverhometeam.com</a></p>

<div class="footer">
  <p>
    <a href="https://thehooverhometeam.com">Website</a> &bull;
    <a href="https://facebook.com/thehooverhometeam">Facebook</a> &bull;
    <a href="https://instagram.com/chrishooverrealtor">Instagram</a>
  </p>
  <p style="margin-top: 10px; font-size: 11px; color: #aaa;">
    You're receiving this because we've worked together or connected about real estate.<br>
    If you'd prefer not to receive these updates, just reply and let me know.
  </p>
</div>

</body>
</html>"""

# Plain text fallback
text_content = """The Hoover Home Team — Weekly Real Estate Update
February 4, 2026

Hey there,

We're already a month into 2026 and the market is starting to pick up steam. I've been out showing properties this week and seeing more buyers getting off the sidelines — which is a great sign. If you've been thinking about making a move, the window is open right now before spring competition heats up.

---

THIS WEEK'S MORTGAGE RATES

30-Year Fixed: 6.20% (down 0.85% from last year)
15-Year Fixed: 5.76% (down 0.69% from last year)
30-Year Jumbo: 6.36% (down 0.98% from last year)

Rates have been holding steady in a tight range. The big story? They're nearly a full point lower than this time last year. On a $400K home, that's roughly $200/month less. If you were priced out before, it's worth running the numbers again.

---

MARKET INSIGHT

Inventory is still tight here in Volusia County, but we're seeing more listings pop up as sellers gear up for spring. Homes priced right are still moving fast — especially in the $300K-$500K range.

For sellers: buyers are out there and motivated. Early spring is historically one of the best times to list.

For buyers: don't wait for rates to be "perfect." Low 6s is solid historically, and you can always refinance later.

---

Thinking about buying or selling? I'd love to chat — even if you're just exploring. No pressure, just a conversation. Hit reply or call anytime.

Talk soon,
Chris Hoover
The Hoover Home Team
thehooverhometeam.com

---
Website: thehooverhometeam.com
Facebook: facebook.com/thehooverhometeam
Instagram: instagram.com/chrishooverrealtor

You're receiving this because we've worked together or connected about real estate.
To unsubscribe, just reply and let me know.
"""

# Build message
msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = "Chris Hoover - The Hoover Home Team <williamstrongthht@gmail.com>"
msg["To"] = "ch@thehooverhometeam.com"

msg.attach(MIMEText(text_content, "plain"))
msg.attach(MIMEText(html_content, "html"))

# Send
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, APP_PASSWORD)
    server.sendmail(EMAIL, ["ch@thehooverhometeam.com"], msg.as_string())
    server.quit()
    print("Newsletter example sent successfully!")
except Exception as e:
    print(f"Error: {e}")
