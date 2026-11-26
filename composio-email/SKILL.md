---
name: composio-email
description: >-
  Interfaces with Gmail and Outlook using Composio to fetch latest emails, search emails, and retrieve email details.
---

# Composio Email Integration

## Overview
This skill allows the agent to fetch, search, and view detailed contents of Gmail and Outlook emails using the Composio API.

## Dependencies
None.

## Quick Start
To list the latest 5 Gmail messages:
```bash
uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py gmail-list --limit 5 --output results.json
```

## Utility Scripts
The Python CLI helper script supports the following commands:
- `gmail-list`: List latest messages or search Gmail.
- `outlook-list`: List latest messages or search Outlook.
- `gmail-detail`: Retrieve full details of a Gmail message by message ID.
- `outlook-detail`: Retrieve full details of an Outlook message by message ID.

### Subcommand Examples:
1. List latest Gmail emails:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py gmail-list --limit 10 --output gmail_latest.json
   ```
2. Search Gmail for a query:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py gmail-list --query "Nintendo" --limit 5 --output gmail_search.json
   ```
3. List latest Outlook emails:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py outlook-list --limit 10 --output outlook_latest.json
   ```
4. Search Outlook for a query:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py outlook-list --query "receipt" --limit 5 --output outlook_search.json
   ```
5. Get Gmail message details:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py gmail-detail --message-id "123456789abcdef" --output email_details.json
   ```
6. Get Outlook message details:
   ```bash
   uv run --with composio-core ~/.gemini/config/skills/composio-email/scripts/check_email.py outlook-detail --message-id "outlook-message-id" --output email_details.json
   ```

## Rate Limiting
This skill respects Composio's rate limits and uses safe execution retries if rate limited.

## Common Mistakes
1. **Missing Environment Variables**: Make sure `COMPOSIO_API_KEY` is present in `~/.env`.
2. **Incorrect Tool Execution User ID**: The script defaults to executing actions using `user_id="user_123"`. Ensure your connected accounts are registered under this user ID in Composio.
