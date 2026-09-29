# phone-conversation

A Claude Code skill for AI agents.

## Install

```bash
# Clone and install
git clone https://example.invalid/review-source
cd agentx
bash skills/install.sh
```

Or manually:
```bash
ln -s /path/to/agentx/skills/phone-conversation "$CLAUDE_CONFIG_DIR/skills/phone-conversation"
```

## What's included

1 scripts:
- `conversation-server.ts` — conversation server

## Usage

- "Call +14155551234 and ask if they're available for dinner"
- "Call the restaurant and make a reservation for 7pm"
- "Call my dentist and reschedule my appointment"
- "Phone the landlord and ask about the maintenance request"
- "Join my Zoom meeting 1234567890"
- "Dial into the meeting and take notes"
- Any time you need AgentX to have a phone conversation or join a meeting on your behalf

## Requirements

- macOS (uses AppleScript for system integrations)
- Claude Code installed

## License

MIT

---

Built by [AgentX](https://example.invalid/review-source) — a personal AI agent platform.
