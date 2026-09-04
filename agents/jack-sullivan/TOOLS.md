# TOOLS.md - Local Notes

## Data Sources

### Volusia County Public Records
- **Clerk of Court:** https://www.clerk.org/ (Laura E. Roth, Clerk of Circuit Court)
- **Property Appraiser:** https://vcpa.vcgov.org/

### FSBO Sources
- Zillow FSBO
- Craigslist (Daytona Beach area)
- Facebook Marketplace

### Power Tools
- **RedX / Vortex** — Expireds, FSBOs, pre-foreclosures. Phone numbers, property data.
  - **Workflow:** Chris exports CSVs (Name, Address, Phone, Email) → Jack enriches & prioritizes against public records
  - No direct API access

### MLS
- *(pending connection)*

### CRM
- **URL:** https://clientlist.onrender.com/
- **Access:** Open (no login required)
- **Capabilities:** View pipeline, add leads, track follow-ups, log activity

---

## Contacts

### William Strong
- **Telegram:** @WilliamStrongBot
- **Role:** Management layer, direct report
- **Delivers:** Daily briefs, coordinates priorities

### Chris Hoover
- **Telegram:** Direct (chat ID: 8560812913)
- **Role:** Founder
- **Escalate:** Urgent leads only

### Ryan Chen
- **Contact:** OpenClaw internal chat only (session: agent:ryan-chen:main)
- **Role:** Technical support / automation
- **Helped with:** Browser automation setup, property lookup automation

---

## Email

- **Address:** jack@thehooverhometeam.com
- Email is handled via /root/agents/bin/send-email.py. Do NOT ask Chris to run mcp or authenticate Gmail. That system no longer exists.
- **Purpose:** All lead outreach + weekly newsletter — professional, representing The Hoover Home Team

### Email Persona
- Write as **Jack Sullivan, assistant to Chris Hoover** — NOT as Chris himself
- First-person voice is Jack's, reaching out on behalf of Chris / The Hoover Home Team
- Example opener: "I'm Jack, Chris Hoover's assistant at The Hoover Home Team..."
- Do NOT impersonate Chris or sign his name

### Signature (use on ALL emails)
```
Jack Sullivan
Assistant to Chris Hoover
The Hoover Home Team powered by REAL LLC
(386) 273-3460
```

---

## Outreach Channels

**Active:** Email only. No SMS platform in use.

---

## Notes

*(Add environment-specific notes here as I learn the tools)*



---

## ⚠️ Email — Do NOT use MCP or Gmail Auth

Never ask Chris (or anyone) to connect MCP or authenticate Gmail.
Use the local email script instead:
```bash
python3 /root/agents/bin/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
```
