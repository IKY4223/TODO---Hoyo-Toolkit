# Drafts: privacy policy and terms of use

Drafts for the owner and a lawyer. They are not legal advice and are not on the site yet. Each
becomes a page in English and Russian once the owner fills the blanks and a lawyer has read
them. Blanks:

- `[NAME]`: who is responsible for the site (a name or a nickname, as the owner decides).
- `[EMAIL]`: the contact address. It will be public on the page.
- `[HOST]`: the hosting provider, and the country its servers are in.
- `[LOG DAYS]`: how long the host keeps server logs.

Written for what the code does in November 2026. Change these texts with the code they describe.

---

## Privacy policy

Last updated: [DATE]

HoYo Toolkit is a fan project run by [NAME]. Write to [EMAIL] with any question about your data,
or to have it deleted.

### What the site handles, and for how long

**Your UID.** When you load a profile, your browser sends the UID to this site's server, which
asks Enka.Network for that player's public showcase. The server keeps the showcase in memory,
never on disk, and reuses it for as long as Enka.Network asks (a minute or more); it is gone once
newer lookups need the room or the server restarts. The UID is part of the address your
browser requests, so it is written in the server's logs, which [HOST] keeps for [LOG DAYS] days.
A failed lookup writes the UID in those logs too.

**Your IP address.** The server counts requests per IP address to stop abuse (an IPv6 address
counts with the rest of its /64 block; behind the host's proxy, it is the address the proxy passes
on). Each count lasts a minute; the address stays in the server's memory, never on disk, until the server restarts or
needs the room. The IP address is also written in the server's logs, kept for [LOG DAYS] days.

**Your wish or warp history link.** The link lets anyone who has it read your history for about
a day. Your browser sends it to this site's server with each page of history it asks for, and
the server passes it to HoYoverse to fetch that page: several times in one import. The server never
stores it or writes it in a log. Your clipboard may keep it after you copy it: on Windows, delete it from the clipboard
history (Win+V) once the import is done.

**Your pulls.** Your imported history stays in your browser's local storage, on your device. It
is not sent to this site's server. So do your theme and language, and the list of relic stats you
mark as wanted. "Delete saved history" removes the history; clearing the site's data in your browser
removes everything. A history file you open is read in your browser and is not uploaded.

**Shared links.** A link to a build carries the player's UID. Whoever has the link sees that
showcase and can tell who shared it. A UID is public in the game, but the link says it is yours.

**Cookies.** The site sets no cookies and runs no analytics or ads.

### Who else receives data

- **Enka.Network** receives the UID from this site's server, not your IP address. Character and
  item images load straight from Enka.Network, so it sees your IP address when your browser
  loads them.
- **HoYoverse** receives your history link from this site's server, when you import.
- **[HOST]** runs the server and keeps its logs.

The calculators (damage, relic odds, wish forecasts) send the numbers you enter, such as a
character's stats, the relic stats you want or your pity, to this site's server. It computes the
answer and keeps nothing.

### The Telegram bot

If you use the bot, Telegram passes this site your Telegram user id, your chat id and your
messages. The bot uses them to answer and does not keep them. A UID you send it reaches
Enka.Network. If you choose a language with /lang, the bot remembers your chat id and the
language; where the bot is set to keep a state file, they are written to disk. Write to [EMAIL]
to have them deleted.

### Your rights

You can ask what data about you the site holds, and have it deleted, at [EMAIL]. The site holds
almost nothing: logs expire after [LOG DAYS] days, and what is on your device is yours to delete.

---

## Terms of use

Last updated: [DATE]

1. HoYo Toolkit is a fan project run by [NAME]. It is not affiliated with, endorsed by or
   sponsored by HoYoverse. Genshin Impact and Honkai: Star Rail, their names, texts and images
   belong to HoYoverse.
2. The site is free and comes with no warranty. Its numbers (damage, forecasts, rates, turn
   orders) are estimates and may be wrong; some rates are community estimates, not published by
   HoYoverse.
3. The game's own terms may not allow third-party tools that read your history or account data.
   You use the history import at your own risk.
4. Do not use the site to look up UIDs in bulk or to collect data about players.
5. The site's own code is under the MIT licence. Third-party notices are in `/notices.txt`.
6. These terms may change; the date above says when they last did. Questions: [EMAIL].

---

## Russian

To be translated once the English text is final, so the lawyer reads one version first.
