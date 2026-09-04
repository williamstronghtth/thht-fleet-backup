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

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'ch@thehooverhometeam.com',
      subject: '✅ Test Email — Profile Pic Check',
      text: `Hey Chris,

Just testing the email setup with my new profile picture!

Let me know if you see my handsome face showing up. 😄

— William`,
      html: `<div style="font-family: Arial, sans-serif;">
<p>Hey Chris,</p>
<p>Just testing the email setup with my new profile picture!</p>
<p>Let me know if you see my handsome face showing up. 😄</p>
<p>— William</p>
</div>`
    });
    
    console.log('✅ Test email sent!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed:', error.message);
  }
}

sendEmail();
