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

  const emailBody = `Hi Julie,

Just following up on Chris's email from Friday regarding the earnest money deposit for 188 River Beach Dr. — wanted to confirm if the escrow has been received and if a receipt is available.

Please let us know when you have a chance!

Thank you,

William Strong
The Hoover Home Team
william@thehooverhometeam.com`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'allfloridatitle@outlook.com',
      cc: 'ch@thehooverhometeam.com',
      subject: 'Re: Brandi and Tye Hollins: Earnest Money Deposit Instructions Request',
      text: emailBody
    });
    
    console.log('✅ Follow-up sent to Julie!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed:', error.message);
  }
}

sendEmail();
