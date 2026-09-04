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

  const emailBody = `Hi Thi,

Just circling back on 6119 Oxbow Bend — wanted to see if your buyers had a chance to view the property yet?

As a reminder, the lockbox code is 1989. We're very motivated to make a deal work, so please let us know if there's any feedback or questions!

Thank you,

William Strong
The Hoover Home Team
william@thehooverhometeam.com`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'kimnguyen1997@kw.com',
      cc: 'ch@thehooverhometeam.com',
      subject: 'Re: 6119 Oxbow Bend - Documents',
      text: emailBody
    });
    
    console.log('✅ Follow-up sent to Thi!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed:', error.message);
  }
}

sendEmail();
