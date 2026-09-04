"""
Jack Sullivan's email signature with embedded headshot.
Import this module into any email script.
"""

HEADSHOT_PATH = "/root/.openclaw/workspace-jack-sullivan/assets/jack-headshot.jpg"

SIGNATURE_HTML = """
<br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, sans-serif;">
  <tr>
    <td style="padding-right: 15px; vertical-align: top;">
      <img src="cid:jackphoto" alt="Jack Sullivan" width="80" height="80" style="border-radius: 50%; object-fit: cover;">
    </td>
    <td style="vertical-align: top;">
      <p style="margin: 0; font-size: 16px; font-weight: bold; color: #1a3a5c;">Jack Sullivan</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">Lead Intelligence Specialist</p>
      <p style="margin: 2px 0; font-size: 13px; color: #555;">The Hoover Home Team powered by REAL LLC</p>
      <p style="margin: 8px 0 0; font-size: 13px;">
        <span style="color: #1a3a5c;">📱</span> <a href="tel:+13862733460" style="color: #1a3a5c; text-decoration: none;">(386) 273-3460</a>
      </p>
      <p style="margin: 2px 0; font-size: 13px;">
        <span style="color: #1a3a5c;">✉️</span> <a href="mailto:jack@thehooverhometeam.com" style="color: #1a3a5c; text-decoration: none;">jack@thehooverhometeam.com</a>
      </p>
    </td>
  </tr>
</table>
"""

def get_headshot_data():
    """Returns the headshot image as bytes."""
    with open(HEADSHOT_PATH, "rb") as f:
        return f.read()

def attach_signature(msg):
    """
    Attaches the signature image to a MIMEMultipart('related') message.
    Call this after attaching the HTML body.
    """
    from email.mime.image import MIMEImage
    
    img = MIMEImage(get_headshot_data())
    img.add_header("Content-ID", "<jackphoto>")
    img.add_header("Content-Disposition", "inline", filename="jack.jpg")
    msg.attach(img)
    return msg
