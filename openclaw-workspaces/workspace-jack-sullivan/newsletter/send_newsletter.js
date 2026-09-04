const nodemailer = require('nodemailer');
const fs = require('fs');

const csv = fs.readFileSync('/root/.openclaw/workspace/crm/client_list_raw.csv', 'utf8');
const emails = [...new Set(
  csv.split('\n')
    .map(line => {
      const cols = line.split(',');
      return (cols[2] || '').trim();
    })
    .filter(e => e.includes('@') && e !== 'Email')
)];

console.log(`Found ${emails.length} unique client emails`);

const today = new Date('2026-04-07T13:00:00Z');
const dateStr = today.toLocaleDateString('en-US', {
  month: 'long',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC'
});

const rate30 = '6.43%';
const change30 = '-0.02%';
const rate15 = '6.01%';
const change15 = '-0.01%';

const subject = `Weekly Market Update: Rates Hold in the Low 6s | ${dateStr}`;

const htmlBody = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Hoover Home Team Weekly</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

<tr>
<td style="background: linear-gradient(135deg, #0f2f4f 0%, #1f5f95 100%); padding:35px 40px; text-align:center;">
  <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:0.4px;">The Hoover Home Team</h1>
  <p style="color:#c6def2;margin:8px 0 0;font-size:14px;letter-spacing:1px;text-transform:uppercase;">Weekly Market Update</p>
  <p style="color:#9fc4e2;margin:6px 0 0;font-size:13px;">${dateStr}</p>
</td>
</tr>

<tr>
<td style="padding:30px 40px 10px;">
  <h2 style="color:#0f2f4f;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">📊 This Week's Mortgage Rates</h2>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="background-color:#f0f6fb;padding:18px 20px;border-radius:6px;width:50%;vertical-align:top;">
        <p style="margin:0;color:#666;font-size:12px;text-transform:uppercase;letter-spacing:1px;">30-Year Fixed</p>
        <p style="margin:5px 0 0;color:#0f2f4f;font-size:32px;font-weight:700;">${rate30}</p>
        <p style="margin:4px 0 0;color:#27ae60;font-size:13px;">▼ ${change30.replace('-', '')} from prior reading</p>
      </td>
      <td width="15"></td>
      <td style="background-color:#f0f6fb;padding:18px 20px;border-radius:6px;width:50%;vertical-align:top;">
        <p style="margin:0;color:#666;font-size:12px;text-transform:uppercase;letter-spacing:1px;">15-Year Fixed</p>
        <p style="margin:5px 0 0;color:#0f2f4f;font-size:32px;font-weight:700;">${rate15}</p>
        <p style="margin:4px 0 0;color:#27ae60;font-size:13px;">▼ ${change15.replace('-', '')} from prior reading</p>
      </td>
    </tr>
  </table>
  <p style="color:#888;font-size:12px;margin:10px 0 0;">Source: Mortgage News Daily daily index, updated 4/6/2026.</p>
</td>
</tr>

<tr>
<td style="padding:25px 40px 10px;">
  <h2 style="color:#0f2f4f;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">🏠 Straight Talk on the Market</h2>
  <p style="color:#333;font-size:15px;line-height:1.75;margin:0 0 14px;">
    Mortgage rates are still hanging in the low 6s, and that matters. A 30-year fixed at <strong>${rate30}</strong> is not the magic number everyone was hoping for a couple of years ago, but it <strong>is</strong> a number buyers can work with when the right property and the right plan come together.
  </p>
  <p style="color:#333;font-size:15px;line-height:1.75;margin:0 0 14px;">
    Here's the real story: markets don't freeze because rates aren't perfect. Deals happen every day because life keeps moving. People relocate, families grow, investors rebalance, and homeowners decide they're ready for something different. The buyers and sellers who win are usually the ones who stay focused on their goals instead of waiting around for headlines to tell them it's safe.
  </p>
  <p style="color:#333;font-size:15px;line-height:1.75;margin:0 0 14px;">
    Around Volusia County, that means opportunity for both sides. Buyers are seeing more choices than they had when inventory was ultra-tight, and sellers who price correctly are still getting real attention. If a home is clean, marketed well, and positioned right, it can absolutely move.
  </p>
  <p style="color:#333;font-size:15px;line-height:1.75;margin:0;">
    The big takeaway this week: <strong>don't let uncertainty keep you on the sidelines if the move itself makes sense.</strong> The best strategy is still the same — know your numbers, understand your timing, and make decisions based on your life, not noise.
  </p>
</td>
</tr>

<tr>
<td style="padding:25px 40px 10px;">
  <h2 style="color:#0f2f4f;font-size:20px;margin:0 0 15px;border-bottom:2px solid #e8e8e8;padding-bottom:10px;">💡 This Week's Advice</h2>
  <div style="background-color:#f8fbff;border-left:4px solid #1f5f95;padding:15px 20px;border-radius:0 6px 6px 0;">
    <p style="color:#333;font-size:15px;line-height:1.75;margin:0;">
      If you're buying, focus less on chasing the perfect rate and more on finding the right property at the right price. Rates can change. Overpaying for the wrong house or missing the right one because you waited too long is harder to fix.
    </p>
  </div>
</td>
</tr>

<tr>
<td style="padding:30px 40px;text-align:center;">
  <p style="color:#333;font-size:16px;line-height:1.7;margin:0 0 20px;">
    If you're thinking about buying, selling, investing, or just want to understand what your next move could look like, reply to this email and we'll point you in the right direction.
  </p>
  <a href="mailto:ch@thehooverhometeam.com" style="display:inline-block;background-color:#0f2f4f;color:#ffffff;text-decoration:none;padding:14px 35px;border-radius:6px;font-size:15px;font-weight:600;letter-spacing:0.3px;">Reply to Chris →</a>
</td>
</tr>

<tr>
<td style="background-color:#f8f8f8;padding:25px 40px;text-align:center;border-top:1px solid #e8e8e8;">
  <p style="color:#0f2f4f;font-weight:700;margin:0 0 5px;font-size:14px;">The Hoover Home Team</p>
  <p style="color:#888;font-size:12px;margin:0 0 3px;">Chris Hoover, Realtor®</p>
  <p style="color:#888;font-size:12px;margin:0 0 3px;">ch@thehooverhometeam.com</p>
  <p style="color:#888;font-size:12px;margin:0 0 15px;">Volusia County, FL</p>
  <p style="color:#aaa;font-size:11px;margin:0;">
    You're receiving this because you've connected with The Hoover Home Team.<br>
    <a href="mailto:ch@thehooverhometeam.com?subject=Unsubscribe" style="color:#999;">Unsubscribe</a>
  </p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>`;

const transporter = nodemailer.createTransport({
  host: 'smtp.gmail.com',
  port: 465,
  secure: true,
  auth: {
    user: 'jack@thehooverhometeam.com',
    pass: 'rpwg sdna xtgp fujn'
  }
});

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
        subject,
        html: htmlBody,
        headers: {
          'List-Unsubscribe': '<mailto:ch@thehooverhometeam.com?subject=Unsubscribe>'
        }
      });
      sent += batch.length;
      console.log(`Batch ${i + 1}/${batches.length} sent (${batch.length} recipients) - ID: ${info.messageId}`);
    } catch (err) {
      failed += batch.length;
      console.error(`Batch ${i + 1} FAILED: ${err.message}`);
    }
    if (i < batches.length - 1) {
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  console.log(`\nDONE: ${sent} sent, ${failed} failed out of ${emails.length} total`);
}

sendAll().catch(console.error);
