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

  const emailBody = `Hi Mark,

I'm reaching out on behalf of Chris Hoover and his family, who are very interested in the property at F88-9 McGettigan Road in Wilton, NH.

They had a couple of questions:

1. How many lots are still available in this development?
2. What would be the cost and feasibility of adding an ADU (Accessory Dwelling Unit) to the property?

For context, Chris is a licensed realtor in New Hampshire and is looking at this for his family's personal use.

Please let us know when you have a chance — happy to set up a call or showing if that's easier.

Thank you!

Best,
William Strong
The Hoover Home Team
william@thehooverhometeam.com

On behalf of Chris Hoover
NH License #`;

  try {
    const info = await transporter.sendMail({
      from: '"William Strong - The Hoover Home Team" <william@thehooverhometeam.com>',
      to: 'Mark@eastkeyrealty.com',
      cc: 'ch@thehooverhometeam.com',
      subject: 'Inquiry: F88-9 McGettigan Road, Wilton NH — Lot Availability & ADU Options',
      text: emailBody
    });
    
    console.log('✅ Email sent to Mark@eastkeyrealty.com!');
    console.log('Message ID:', info.messageId);
  } catch (error) {
    console.error('❌ Failed:', error.message);
  }
}

sendEmail();
