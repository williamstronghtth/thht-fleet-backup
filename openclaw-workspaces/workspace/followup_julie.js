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

Just wanted to follow up on Chris's email from yesterday — wanted to make sure it didn't get buried in your inbox!

Please let us know when you have a chance. Happy to work around your schedule.

Thanks!

Best,
William Strong
The Hoover Home Team
william@thehooverhometeam.com`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'julie@titlecompany.com', // placeholder - need actual email
      cc: 'ch@thehooverhometeam.com',
      subject: 'Re: Following Up',
      text: emailBody
    });
    
    console.log('✅ Follow-up sent to Julie!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed:', error.message);
  }
}

sendEmail();
