const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// Read email list from CSV
const csv = fs.readFileSync('/root/.openclaw/workspace/crm/client_list_raw.csv', 'utf8');

// Read unsubscribed list
let unsubscribed = [];
const unsubFile = '/root/.openclaw/workspace/crm/unsubscribed.txt';
if (fs.existsSync(unsubFile)) {
  unsubscribed = fs.readFileSync(unsubFile, 'utf8')
    .split('\n')
    .map(e => e.trim().toLowerCase())
    .filter(e => e.length > 0);
}

const emails = [...new Set(
  csv.split('\n')
    .map(line => {
      const cols = line.split(',');
      return (cols[2] || '').trim();
    })
    .filter(e => e.includes('@') && e !== 'Email' && !unsubscribed.includes(e.toLowerCase()))
)];

console.log(`Found ${emails.length} unique client emails (${unsubscribed.length} unsubscribed excluded)`);

const today = new Date('2026-04-07');
const dateStr = today.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

const htmlBody = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Hoover Home Team Weekly</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

<!-- Header -->
<tr>
<td style="background: linear-gradient(135deg, #1a3a5c 0%, #2d5f8a 100%); padding:35px 40px; text-align:center;">
  <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:0.5px;">The Hoover Home Team</h1>
  <p style="color:#a8cce8;margin:8px 0 0;font-size:14px;letter-spacing:1px;text-transform:uppercase;">Weekly Market Update</p>
  <p style="color:#7fb3d8;margin:6px 0 0;font-size:13px;">${dateStr}</p>
</td>
</tr>

<!-- Mortgage Rates -->
<tr>
<td style="padding:30px 40px 10px;">
  <h2 style="color:#1a3a5c;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">📊 This Week's Mortgage Rates</h2>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="background-color:#f0f6fb;padding:18px 20px;border-radius:6px;width:50%;">
        <p style="margin:0;color:#666;font-size:12px;text-transform:uppercase;letter-spacing:1px;">30-Year Fixed</p>
        <p style="margin:5px 0 0;color:#1a3a5c;font-size:32px;font-weight:700;">6.43%</p>
        <p style="margin:4px 0 0;color:#27ae60;font-size:13px;">▼ 0.02% from last week</p>
      </td>
      <td width="15"></td>
      <td style="background-color:#f0f6fb;padding:18px 20px;border-radius:6px;width:50%;">
        <p style="margin:0;color:#666;font-size:12px;text-transform:uppercase;letter-spacing:1px;">15-Year Fixed</p>
        <p style="margin:5px 0 0;color:#1a3a5c;font-size:32px;font-weight:700;">6.01%</p>
        <p style="margin:4px 0 0;color:#27ae60;font-size:13px;">▼ 0.01% from last week</p>
      </td>
    </tr>
  </table>
  <p style="color:#888;font-size:12px;margin:10px 0 0;">Source: Mortgage News Daily, ${dateStr}</p>
</td>
</tr>

<!-- Market Insights -->
<tr>
<td style="padding:25px 40px 10px;">
  <h2 style="color:#1a3a5c;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">🏠 Volusia County Market Pulse</h2>
  <p style="color:#333;font-size:15px;line-height:1.7;margin:0 0 12px;">
    Rates continue to inch downward, and that's great news for anyone watching the market. The 30-year fixed dropped to 6.43% this week. It's not a dramatic move, but the trend has been steady — and buyers are noticing.
  </p>
  <p style="color:#333;font-size:15px;line-height:1.7;margin:0 0 12px;">
    Here in Volusia County, spring inventory is picking up. Port Orange and Ormond Beach are seeing more listings come on, which gives buyers room to breathe. But the best homes — priced right and in good shape — are still getting offers within the first week or two.
  </p>
  <p style="color:#333;font-size:15px;line-height:1.7;margin:0;">
    If you've been on the fence about selling, this is a window worth paying attention to. Buyer activity is climbing, rates are cooperating, and there's less competition from other sellers right now than there will be in a few weeks.
  </p>
</td>
</tr>

<!-- Tip of the Week -->
<tr>
<td style="padding:25px 40px 10px;">
  <h2 style="color:#1a3a5c;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">💡 Tip of the Week</h2>
  <div style="background-color:#fef9e7;border-left:4px solid #f0b429;padding:15px 20px;border-radius:0 6px 6px 0;">
    <p style="color:#333;font-size:15px;line-height:1.7;margin:0;">
      <strong>Thinking about selling? Start with a pre-listing inspection.</strong> Most sellers wait for the buyer's inspection and then scramble to negotiate repairs. Getting your own inspection first puts you in control. You can fix things on your terms, price accordingly, and avoid surprises that blow up deals. It typically costs $300 to $500 and can save you thousands in negotiations.
    </p>
  </div>
</td>
</tr>

<!-- CTA -->
<tr>
<td style="padding:30px 40px;text-align:center;">
  <p style="color:#333;font-size:16px;line-height:1.6;margin:0 0 20px;">
    Whether you're buying, selling, or just curious about your home's value — we're here to help.
  </p>
  <a href="mailto:ch@thehooverhometeam.com" style="display:inline-block;background-color:#1a3a5c;color:#ffffff;text-decoration:none;padding:14px 35px;border-radius:6px;font-size:15px;font-weight:600;letter-spacing:0.5px;">Get in Touch →</a>
</td>
</tr>

<!-- Footer -->
<tr>
<td style="background-color:#f8f8f8;padding:25px 40px;text-align:center;border-top:1px solid #e8e8e8;">
  <p style="color:#1a3a5c;font-weight:700;margin:0 0 5px;font-size:14px;">The Hoover Home Team</p>
  <p style="color:#888;font-size:12px;margin:0 0 3px;">Chris Hoover, Realtor®</p>
  <p style="color:#888;font-size:12px;margin:0 0 3px;">ch@thehooverhometeam.com</p>
  <p style="color:#888;font-size:12px;margin:0 0 15px;">Volusia County, FL</p>
  <p style="color:#aaa;font-size:11px;margin:0;">
    You're receiving this because you've connected with The Hoover Home Team.<br>
    <a href="mailto:jack@thehooverhometeam.com?subject=Unsubscribe" style="color:#999;">Unsubscribe</a>
  </p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>`;

// Configure SMTP - Jack Sullivan
const transporter = nodemailer.createTransport({
  host: 'smtp.gmail.com',
  port: 465,
  secure: true,
  auth: {
    user: 'jack@thehooverhometeam.com',
    pass: 'rpwg sdna xtgp fujn'
  }
});

// Send in batches of 50 (BCC limit best practice)
const BATCH_SIZE = 50;
const batches = [];
for (let i = 0; i < emails.length; i += BATCH_SIZE) {
  batches.push(emails.slice(i, i + BATCH_SIZE));
}

async function sendAll() {
  console.log(`Sending to ${emails.length} recipients in ${batches.length} batches...`);
  let sent = 0;
  let failed = 0;

  for (let i = 0; i < batches.length; i++) {
    const batch = batches[i];
    try {
      const info = await transporter.sendMail({
        from: '"The Hoover Home Team" <jack@thehooverhometeam.com>',
        to: 'jack@thehooverhometeam.com',
        cc: 'ch@thehooverhometeam.com',
        bcc: batch.join(', '),
        subject: `🏠 Weekly Market Update — Rates at 6.43% | ${dateStr}`,
        html: htmlBody,
        headers: {
          'List-Unsubscribe': '<mailto:jack@thehooverhometeam.com?subject=Unsubscribe>'
        }
      });
      sent += batch.length;
      console.log(`Batch ${i + 1}/${batches.length} sent (${batch.length} recipients) - ID: ${info.messageId}`);
    } catch (err) {
      failed += batch.length;
      console.error(`Batch ${i + 1} FAILED:`, err.message);
    }
    // Small delay between batches
    if (i < batches.length - 1) {
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  console.log(`\nDONE: ${sent} sent, ${failed} failed out of ${emails.length} total`);
}

sendAll().catch(console.error);
