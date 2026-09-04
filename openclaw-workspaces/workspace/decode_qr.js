const Jimp = require('jimp');
const QRCodeReader = require('qrcode-reader');

async function decodeQR() {
  const image = await Jimp.read('/root/.openclaw/workspace/2fa_qr.png');
  
  const qr = new QRCodeReader();
  
  return new Promise((resolve, reject) => {
    qr.callback = (err, value) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(value);
    };
    qr.decode(image.bitmap);
  });
}

decodeQR()
  .then(result => {
    console.log('QR Code decoded successfully!');
    console.log('\nFull content:');
    console.log(result.result);
    
    // Parse the TOTP URL
    const url = new URL(result.result);
    console.log('\nParsed:');
    console.log('  Protocol:', url.protocol);
    console.log('  Label:', decodeURIComponent(url.pathname.slice(1)));
    console.log('  Secret:', url.searchParams.get('secret'));
    console.log('  Issuer:', url.searchParams.get('issuer'));
  })
  .catch(err => {
    console.error('Error decoding QR:', err);
  });
