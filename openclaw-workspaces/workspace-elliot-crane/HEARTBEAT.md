# HEARTBEAT.md

# ACTIVE — Resumed 2026-05-11 per Chris authorization

## Checklist (rotate through, 2-4x per day)
- [ ] Emails — any urgent unread?
- [ ] Calendar — events in next 24-48h?
- [ ] Scanner logs — any actionable alerts? (`tail -20 /tmp/elliot-scanner.log`)
- [ ] Spike alerts — any flagged moves? (`tail -20 /tmp/elliot-alert.log`)

## Crons Active
- Hourly scanner: 7am-10pm ET at :00
- Spike alert: 7am-10pm ET at :05
- News monitor: every 10 min (7am-10pm ET)
