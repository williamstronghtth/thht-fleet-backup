const nodemailer = require('nodemailer');

// Extract emails from the raw list - manually curated from CSV
const emails = [
  '06brittany@gmail.com', 'aldenjones@bellsouth.net', 'fhudak@tampabay.rr.com',
  'svctech398@yahoo.com', 'joefarino@comcast.net', 'jjharding@metrocast.net',
  'sjander228@aol.com', 'gboynton2003@gmail.com', 'annatrendler47@gmail.com',
  'davidjkwiat@cfl.rr.com', 'ravesdesign@prodigy.net', 'mikethenice713@aol.com',
  'josephjeff314@gmail.com', 'jennifer.melise@yahoo.com', 'gerjem@yahoo.com',
  'dorenardjean@gmail.com', 'hankevans528@gmail.com', 'noelmartin1955@gmail.com',
  'sj54sj54j54@gmail.com', 'martinwillie@currently.com', 'teleshia51@gmail.com',
  'leggettt760@gmail.com', 'adaobertson554@yahoo.com', 'brave.enelas@yahoo.com',
  'norman.cummings.5.2024@gmail.com', 'n2ryan@yahoo.com', 'avgumbs@yahoo.com',
  'glenda.pierson@aol.com', 'will2b3@gmail.com', 'avswamy@gmail.com',
  'reichmanguercy@gmail.com', 'chrisholmes319@yahoo.com', 'vcurc@aol.com',
  'briancheshire25@gmail.com', 'tksunil@yahoo.com', 'virgoo53@yahoo.com',
  'jpike22018@gmail.com', 'bdbrown3222@gmail.com', 'micaldridge@comcast.net',
  'mccollumk2013@gmail.com', 'nortilien27@gmail.com', 'prschoeck@gmail.com',
  'sdffla@gmail.com', 'tomdonhen@yahoo.com', 'Christinehrobinson@gmail.com',
  'Pforeman2008@hotmail.com', 'mygman02@yahoo.com', 'salvador.lee@verizon.net',
  'brianwilkie11@hotmail.com', 'hannaharivera@outlook.com', 'michaeldamon1970@gmail.com',
  'wlatkinson3@outlook.com', 'mschneider2263@gmail.com', 'ozyldrm.fet@gmail.com',
  'tamuyennguyen1603@gmail.com', 'suzymunnis@live.com', 'anna_76133@yahoo.com',
  'dulyma@hotmail.com', 'miketinker@live.com', 'barbaracauley1@outlook.com',
  'DMcPherjr@gmail.com', 'jpier@stny.rr.com', 'amberkirtley.avonrep@gmail.com',
  'Mrsluita@gmail.com', 'jillmbax@gmail.com', 'ff.palmer@yahoo.com',
  'sandycross7@yahoo.com', 'brandileighmaz@gmail.com', 'eulven16@gmail.com',
  'kelli@tuckerinsgroup.com', 'suemacc@att.net', 'cmpollino2123@gmail.com',
  'floridaroadrep@gmail.com', 'ahammacher@playalargoresort.com',
  'ardmishu@yahoo.com', 'dtr1909@verizon.net', 'mgbrisco@gmail.com',
  'rosawilson@gmail.com', 'brady.lessard@sanfordfl.gov', 'gattshjc@gm.sbac.edu',
  'beckywhite1230@gmail.com', 'j_stagnari@bellsouth.net', 'fmacklin@cfl.rr.com',
  'ardenrcmll@gmail.com', 'bigwes0910@gmail.com', 'joe@directmillworkusa.com',
  'cayla.poborsky@gmail.com', 'Kshiflett1966@gmail.com', 'cjsemplice@frontier.com',
  'ozziej5@yahoo.com', 'abbybart@aol.com', 'abi61@hotmail.com', 'adi2@live.com',
  'akubes@collegeclub.com', 'akubes@prodigy.net', 'amber.wyborny@aol.com',
  'americkso@gmail.com', 'ampy36@hotmail.com', 'amykondrat@yahoo.com',
  'anarchiest27@hotmail.com', 'angelatromp13@gmail.com', 'anitabba@hotmail.com',
  'anne.bussegandt@gmail.com', 'anne.sprucecreek@gmail.com', 'anthony.brisbane@yahoo.com',
  'anthonybrisba@mybluelight.com', 'aziendragon@gmail.com', 'bakbulut@netscape.net',
  'barbaradlubac@yahoo.com', 'barbaramelnick@gmail.com', 'barbvlaven@yahoo.com',
  'baswell_a@yahoo.com', 'bdevane@epix.net', 'bdevanejr@yahoo.com', 'bdglenn38@yahoo.com',
  'beycan@prodigy.net', 'bgilligan0184@hotmail.com', 'billhellums@gmail.com',
  'bittnervending@shol.com', 'boonedonna47@gmail.com', 'bowlingme@aol.com',
  'bubbaw1031@aol.com', 'cardin@aol.com', 'ccastle2@yahoo.com', 'cccdennis9494@yahoo.com',
  'ccristaldi@att.net', 'chadshazen@hazenconstruction.net', 'charleakonanl@gmail.com',
  'chlmom@hotmail.com', 'chlmom@msn.com', 'choupe@gte.net', 'ciesluk@cs.com',
  'clukas5768@live.com', 'colesonner@gmail.com', 'cpkingsqueen@gmail.com',
  'cris@morningstarhomes.com', 'csfarina@verizon.net', 'cubalibras@gmail.com',
  'cwburt@hotmail.com', 'cwilary@gmail.com', 'cwilary@yahoo.com', 'dabell17@alltel.com',
  'dago1123@mail.com', 'daplin@roadrunner.com', 'darenmaas@texasag.com',
  'dblogan1954@verizon.net', 'decrapio@gremlan.org', 'dgalkin1@hotmail.com',
  'diblingm@aol.com', 'digitalrico@gmail.com', 'dmitriygalkin@gmail.com', 'dml7198@aol.com',
  'donna.clark@uswest.net', 'donnabswim0202@gmail.com', 'dpganung@yahoo.com',
  'dr.barbaralavender@yahoo.com', 'drericlo@yahoo.com', 'dspifer59@gmail.com',
  'duchesspat@frontier.com', 'dustyc30@gmail.com', 'ebkf11@yahoo.com', 'ebradley@qix.net',
  'eeriecalm@adelphia.net', 'elanadahaman@hotmail.com', 'elicia.connors@hologic.com',
  'eliciaconnors@yahoo.com', 'eric@ericlo.net', 'esg3559@aol.com', 'evabowling@aol.com',
  'fatkid50@comcast.net', 'fcsanch10@aol.com', 'fcsanch@aol.com', 'fdxfreightdog@gmail.com',
  'gdlibertya87@bright.net', 'glenn4479@gmail.com', 'gwilli1958@bellsouth.net',
  'helty_1995@hotmail.com', 'hlesenskyj@hotmail.com', 'ikharysi2@aol.com', 'j11795@aol.com',
  'jacobneskora@gmail.com', 'jane.chen24@gmail.com', 'janepeterc@yahoo.com', 'janual@aol.com',
  'jazmen9@aol.com', 'jcorwin@frontiernet.net', 'jd441444@gmail.com', 'jdesposito2@cfl.rr.com',
  'jdublas@aol.com', 'jessica.eckelbarger@gmail.com', 'jessicaeckelbarger@gmail.com',
  'jessikacohen@bellsouth.net', 'jgibson2@nycap.rr.com', 'jgriffith46675@aol.com',
  'jgriffith@ptd.net', 'jjtaabba@comcast.net', 'jkroeplin@gmail.com', 'jlheltemes@frontiernet.net',
  'jma121@suddenlink.net', 'jmeireles@att.net', 'joan.anthony@gmail.com', 'joeandpamw@yahoo.com',
  'joew_ski@yahoo.com', 'johno@rochester.rr.com', 'jorge_qv@yahoo.com',
  'jquinones-vigo@collegeclub.com', 'jrbaird@comcast.net', 'jrbaird@usa.net',
  'justicek@ignite2x.com', 'jwcagent@gmail.com', 'karen.gallo@hotmail.com',
  'karenggallo@gmail.com', 'kaw.wiseman@gmail.com', 'kawwiseman@gmail.com',
  'keishla.ortiz90@gmail.com', 'kimbitner@yahoo.com', 'kimbobp@comcast.net',
  'kthomas07@gmail.com', 'kuher@optonline.net', 'ladonna.kersten18@bellsouth.net',
  'lance.oscarson@thomasarts.com', 'larsandcarole@aol.com', 'larsofdb@aol.com',
  'laura_gorgone@hotmail.com', 'laurai33@embarqmail.com', 'lbjab@juno.com',
  'leahboynton@yahoo.com', 'lenansb@aol.com', 'leseck@yahoo.com', 'lifeisgoood@me.com',
  'llacombe@pcigroup.com', 'lleseck@comcast.net', 'lmothersell@gmail.com', 'lnkpeacock@aol.com',
  'lostpc@aol.com', 'lsternal@yahoo.com', 'luisrodriguez176@gmail.com', 'lukas711@bellsouth.net',
  'mae704@bellsouth.net', 'mando900@yahoo.com', 'margiej19@yahoo.com', 'marshmama@roadrunner.com',
  'marshmama@yahoo.com', 'matt@teaminternational.com', 'matthew.moore@cableone.net',
  'mcalache@aol.com', 'mdibling@comcast.net', 'meghanschook@gmail.com', 'michaeltek25@gmail.com',
  'michelleconero@gmail.com', 'mike.bartlett@employeebenefitsllc.net', 'miltonmom44@yahoo.com',
  'minawi@rogers.com', 'moezot4x@hotmail.com', 'mrs44casey@yahoo.com', 'mylove4497@gmail.com',
  'mztee0105@gmail.com', 'nailchris@gmail.com', 'nanceflowers@yahoo.com',
  'nathanfackrell@outlook.com', 'nfackrell@aol.com', 'nicarino@aol.com', 'niftytifty16@hotmail.com',
  'nmdano@aol.com', 'nowaczck@yahoo.com', 'nowdenpc@chartermi.net', 'nsbbunny@aol.com',
  'nsbbunny@gte.net', 'olivia.katrandjian@gmail.com', 'partovi.ar@gmail.com',
  'partoviar@gmail.com', 'patriciata@aol.com', 'patriciatremblay@gmail.com',
  'peacefuldays59@gmail.com', 'rah43pt26@aol.com', 'rayhopkins1202@comcast.net',
  'rballent@wideopenwest.com', 'rcferuch@comcast.net', 'reskdz@aol.com', 'reskdz@msn.com',
  'rilwanbalogun97@gmail.com', 'rita.oliva@att.net', 'ritaoliva@gmail.com', 'river317@umn.edu',
  'rjbul42647@aol.com', 'ronald.kuehn@hotmail.com', 'roselindaricca@gmail.com',
  'rricca@malverne.k12.ny.us', 'rsheynblat@hotmail.com', 'rufus947@gmail.com',
  'rykel@optonline.net', 'sales@wedowindowsusa.com', 'sandybeach1025@att.net',
  'sbargen@bargeninc.com', 'selliottfomi@hotmail.com', 'sharkjaws5@aol.com',
  'sherri@bargeninc.com', 'siennaburgos@gmail.com', 'smeaderzz4@yahoo.com', 'smutt913@hotmail.com',
  'spaqueen053@gmail.com', 'steve@lakwarehouse.com', 'sumthjingu@yahoo.com', 'swissal@aol.com',
  'tangela@tpi.to', 'tcalache@lycos.com', 'thahn@nd.edu', 'thallow@twcny.rr.com',
  'thallow@yahoo.com', 'thellums@gmail.com', 'thetek4@aol.com', 'thomas2876@hotmail.com',
  'tlnsb3354@gmail.com', 'tongue_tied_66@yahoo.com', 'topsk8er911@aol.com',
  'tracey.hahn@yahoo.com', 'tss7859@gmail.com', 'universityrehabpo@gmail.com',
  'varkias4@aol.com', 'vdeleon1603@gmail.com', 'vroger.hillv42@ameritech.net',
  'waters864@gmail.com', 'wedo1michael@live.com', 'wmtina@hotmail.com',
  'ybarnett-kearns@aol.com', 'ykearns@optonline.net', 'zrcat@airadv.net',
  'turkfritts@aol.com', 'rzibell@gmail.com', 'ghenze@hotmail.com', 'tcalkins@avci.net'
];

// Remove duplicates
const uniqueEmails = [...new Set(emails.map(e => e.toLowerCase()))];

const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Hoover Home Team Weekly</title>
</head>
<body style="margin: 0; padding: 0; font-family: Georgia, 'Times New Roman', serif; background-color: #f5f5f5;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); padding: 30px 40px; text-align: center;">
              <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: normal;">The Hoover Home Team</h1>
              <p style="color: #90cdf4; margin: 10px 0 0 0; font-size: 16px;">Weekly Real Estate Update</p>
            </td>
          </tr>
          
          <!-- Date -->
          <tr>
            <td style="padding: 20px 40px 10px; text-align: center; border-bottom: 1px solid #e2e8f0;">
              <p style="color: #718096; margin: 0; font-size: 14px;">March 17, 2026</p>
            </td>
          </tr>
          
          <!-- Mortgage Rates Section -->
          <tr>
            <td style="padding: 30px 40px;">
              <h2 style="color: #1a365d; margin: 0 0 15px 0; font-size: 22px; border-bottom: 2px solid #4299e1; padding-bottom: 10px;">📊 Mortgage Rate Update</h2>
              <p style="color: #4a5568; line-height: 1.7; margin: 0;">
                <strong>Good news for buyers!</strong> Mortgage rates dropped 0.06% on Monday as oil prices fell more than 5%. The bond market responded positively, and 30-year fixed rates are now at 3-month lows after reaching 7-month highs just last Friday.
              </p>
              <div style="background-color: #ebf8ff; border-left: 4px solid #4299e1; padding: 15px 20px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                <p style="margin: 0; color: #2c5282; font-size: 15px;">
                  <strong>What this means:</strong> If you've been waiting for rates to stabilize, this week's drop signals a potential opportunity. Let's talk about locking in before the next shift.
                </p>
              </div>
            </td>
          </tr>
          
          <!-- Recent Wins Section -->
          <tr>
            <td style="padding: 0 40px 30px;">
              <h2 style="color: #1a365d; margin: 0 0 15px 0; font-size: 22px; border-bottom: 2px solid #48bb78; padding-bottom: 10px;">🏆 Recent Wins</h2>
              
              <div style="background-color: #f0fff4; padding: 20px; border-radius: 6px; margin-bottom: 15px;">
                <p style="margin: 0 0 5px 0; color: #276749; font-weight: bold;">✅ CLOSED: 209 Tarracina Way, Daytona Beach</p>
                <p style="margin: 0; color: #4a5568;">Closed March 9th at $225,000. Happy to help close friends find their perfect home!</p>
              </div>
              
              <div style="background-color: #f0fff4; padding: 20px; border-radius: 6px; margin-bottom: 15px;">
                <p style="margin: 0 0 5px 0; color: #276749; font-weight: bold;">✅ CLOSED: 188 River Beach Dr, Ormond Beach</p>
                <p style="margin: 0; color: #4a5568;">Closed March 2nd. Our buyers beat out 3 competing offers!</p>
              </div>
              
              <div style="background-color: #fefcbf; padding: 20px; border-radius: 6px;">
                <p style="margin: 0 0 5px 0; color: #975a16; font-weight: bold;">📝 UNDER CONTRACT: 6119 Oxbow Bend Lane, Port Orange</p>
                <p style="margin: 0; color: #4a5568;">Now at $750,000 (reduced from $775K). Moving toward closing!</p>
              </div>
            </td>
          </tr>
          
          <!-- Market Insight -->
          <tr>
            <td style="padding: 0 40px 30px;">
              <h2 style="color: #1a365d; margin: 0 0 15px 0; font-size: 22px; border-bottom: 2px solid #ed8936; padding-bottom: 10px;">🏠 Volusia County Market Insight</h2>
              <p style="color: #4a5568; line-height: 1.7; margin: 0 0 15px 0;">
                Spring is here and the market is heating up. We're seeing multiple offer situations return on well-priced homes, especially in Port Orange, Ormond Beach, and New Smyrna Beach.
              </p>
              <p style="color: #4a5568; line-height: 1.7; margin: 0;">
                <strong>For sellers:</strong> Inventory remains tight. If you've been considering a move, now is an excellent time to list while buyer demand is strong.
              </p>
              <p style="color: #4a5568; line-height: 1.7; margin: 15px 0 0 0;">
                <strong>For buyers:</strong> Be prepared to move quickly on homes you love. Get pre-approved and have your documents ready.
              </p>
            </td>
          </tr>
          
          <!-- CTA -->
          <tr>
            <td style="padding: 0 40px 30px; text-align: center;">
              <div style="background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); padding: 25px; border-radius: 8px;">
                <p style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px;">Thinking about making a move?</p>
                <p style="color: #e2e8f0; margin: 0 0 20px 0; font-size: 14px;">Let's have a quick chat about your options. No pressure, just honest advice.</p>
                <a href="mailto:ch@thehooverhometeam.com" style="display: inline-block; background-color: #ffffff; color: #3182ce; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reply to This Email</a>
              </div>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="background-color: #1a365d; padding: 25px 40px; text-align: center;">
              <p style="color: #ffffff; margin: 0 0 5px 0; font-size: 16px; font-weight: bold;">Chris Hoover</p>
              <p style="color: #90cdf4; margin: 0 0 10px 0; font-size: 14px;">The Hoover Home Team</p>
              <p style="color: #a0aec0; margin: 0; font-size: 12px;">
                Licensed in Florida, Massachusetts & New Hampshire<br>
                (386) 212-7420 | ch@thehooverhometeam.com<br>
                thehooverhometeam.com
              </p>
            </td>
          </tr>
          
          <!-- Unsubscribe -->
          <tr>
            <td style="padding: 15px 40px; text-align: center; background-color: #f7fafc;">
              <p style="color: #a0aec0; margin: 0; font-size: 11px;">
                You're receiving this because you're part of The Hoover Home Team community.<br>
                Reply with "unsubscribe" if you'd prefer not to receive these updates.
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`;

async function sendNewsletter() {
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      user: 'william@thehooverhometeam.com',
      pass: 'jvjnairgefinleph'
    }
  });

  const mailOptions = {
    from: '"William Strong | The Hoover Home Team" <william@thehooverhometeam.com>',
    to: 'william@thehooverhometeam.com',
    cc: 'ch@thehooverhometeam.com',
    bcc: uniqueEmails.join(', '),
    subject: '🏠 Weekly Update: Rates Drop, Spring Market Heats Up',
    html: htmlContent
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    console.log('Newsletter sent successfully!');
    console.log('Message ID:', info.messageId);
    console.log('Recipients:', uniqueEmails.length);
    return { success: true, messageId: info.messageId, recipientCount: uniqueEmails.length };
  } catch (error) {
    console.error('Error sending newsletter:', error);
    return { success: false, error: error.message };
  }
}

sendNewsletter().then(result => {
  console.log(JSON.stringify(result, null, 2));
});
