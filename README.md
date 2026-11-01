# Telegram Support Bot

## 1. Create the bot

1. Open Telegram and message **@BotFather**.
2. Send `/newbot`.
3. Choose a display name, for example `ANYAI Support`.
4. Choose a username ending in `bot`, for example `anyaistore_support_bot`.
5. Copy the token BotFather gives you. Never publish it.

## 2. Find your owner chat ID

Message **@userinfobot** from your personal Telegram account and copy the numeric ID.

## 3. Run

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

Edit `.env` with your token and numeric owner ID, then run:

```bash
python support_bot.py
```

The bot stores every owner-message ID to customer ID in `support.sqlite3`. Reply to the forwarded customer message in your owner chat; the bot sends the reply only to that customer.
