const nodemailer = require('nodemailer');

async function sendEmail() {
  // Create transporter with Google Workspace SMTP
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      user: 'william@thehooverhometeam.com',
      pass: 'n7J>=A8MbG*Y5mD&'
    }
  });

  const emailBody = `Hi Rob,

I wanted to reach out and introduce myself — I'm William Strong, and I work alongside Chris Hoover at The Hoover Home Team.

Chris speaks highly of his time at Coldwell Banker, and I know he values the relationships he built there. I'm reaching out to let you know we're always here if there's anything we can help with — whether it's a referral, market insights, or just connecting on a deal.

Looking forward to staying in touch!

Best,
William Strong
The Hoover Home Team
william@thehooverhometeam.com`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'rob@cbccr.com',
      cc: 'ch@thehooverhometeam.com',
      subject: 'Introduction from The Hoover Home Team',
      text: emailBody
    });
    
    console.log('✅ Email sent! Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed to send:', error.message);
    if (error.message.includes('Username and Password not accepted')) {
      console.log('\nNeed to either:');
      console.log('1. Generate an App Password in Google Account settings');
      console.log('2. Or enable "Less secure app access" (not recommended)');
    }
  }
}

sendEmail();
