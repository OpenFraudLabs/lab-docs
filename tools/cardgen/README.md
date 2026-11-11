# CheckAm warning card maker

Makes the shareable scam warning cards in `assets/checkam/cards/` (square 1080x1080 and status 1080x1920).
This folder is excluded from the website build (`_config.yml`), so it is never served.

Rules for every card: it shows a scam type with an example we wrote, blurred. Never a real message,
person, account number, phone number or business.

To add or change a card:
1. Edit `cards.json` (key, code, kind "rule" or "campaign", title, example, two signs, todo).
2. In this folder: `npm i @fontsource/inter@5.1.0` and copy `../../assets/logo-round.png` here.
3. `node render.js ../../assets/checkam/cards [key]` (Playwright with Chromium).
4. Add the card to the `warning_cards` table (same key and code) so the bot and admin know it.
