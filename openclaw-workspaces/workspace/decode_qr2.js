const sharp = require('sharp');
const jsQR = require('jsqr');

async function decodeQR() {
  // Load image and get raw pixel data
  const image = sharp('/root/.openclaw/workspace/2fa_qr.png');
  const { data, info } = await image.raw().ensureAlpha().toBuffer({ resolveWithObject: true });
  
  console.log('Image size:', info.width, 'x', info.height);
  
  // Decode QR code
  const code = jsQR(new Uint8ClampedArray(data), info.width, info.height);
  
  if (code) {
    console.log('\n✅ QR Code decoded!');
    console.log('\nFull content:');
    console.log(code.data);
    
    // Parse the TOTP URL
    try {
      const url = new URL(code.data);
      console.log('\n--- Parsed TOTP URL ---');
      console.log('Protocol:', url.protocol);
      console.log('Type:', url.host);
      console.log('Label:', decodeURIComponent(url.pathname.slice(1)));
      console.log('Secret:', url.searchParams.get('secret'));
      console.log('Issuer:', url.searchParams.get('issuer'));
    } catch (e) {
      console.log('Could not parse as URL');
    }
  } else {
    console.log('❌ No QR code found in image');
  }
}

decodeQR().catch(console.error);
