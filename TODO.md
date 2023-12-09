# WieeRd's TODO note

Oh my god there is so much things to do

## -1. GET THIS FUCKING WORKING AGAIN

1. Catch up discord.py API changes
2. Revise outdated dependencies
3. Database client & migration
4. Find proper package/project manager for Python
5. Inspect all the TODOs below and organize them

## 0. Priority Tasks

1. Game module
2. Dropdown Help command
3. Setup Logging
4. Feedback module
5. QRCode, MagicConch

## 1. New Stuff

### 1.1. New Module

* Game
  * Chess
  * TicTacToe
  * RockPaperScissor
* Custom
  * create custom command (per server)
  * tag command (R. Danny)
* Portal
  * Link channels using webhook
* Statistic
  * command usage
  * network visualization
    * pyvis is inefficient as hell, gotta code myself

### 1.2. New Command

* Tools
  * QRcode generator
  * Starboard
  * Mute / SelfMute
  * get sticker asset
  * Anti Raid / Spam (R. Danny)
* Pranks
  * MagicConch
  * Mention shield, karma
* Owner
  * Update announcement
  * Send feedback
  * Bot profile editing

### 1.3. New Feature

* Help command
  * Dropdown Help command
  * Dump as markdown document (README.md)
  * Send help when mentioned
* Logging
  * seperate stdout/stderr
  * on_error() Handler
* Converter
  * Fuzzy search
    * improve performance
    * add timeout
  * Time (HH:MM)
  * Guild (fuzzy, mutual)
* Internationalization
  * clockbot.command
    * utilize command.extras
    * different attrs per locale
    * locale decorator
  * get_locale()
    * preferred locale (community guild)
    * ctx.invoked_with
    * DB (per guild / user)
* Database
  * Should have used MariaDB tbh
  * NullDB, JsonDB: To continue without DB

## 2. Improvements

* Mention
  * easier expression
* Voice
  * ClockBot.js
    * rewrite voice-related features with discord.js
  * Music
    * voice command
  * TTS
    * kakao speech
    * change voice
    * sound effect
    * voice overlapping
  * stage channel support
* Pranks
  * Custom message for each filter
  * Preserve text objects (mention, emoji, ...)
  * New filters
    * Chaos
    * Mirror (vertical & horizontal)
    * NyanChat
    * Hawawa
  * Bonk
    * more distortion per "bonk"
    * more variants (kkang, RIP, triggered)
    * support file attachments
  * Revive google translation feature
* Clock
  * Better delay mechanic
* Bamboo
  * Usage count
  * Logging on/off
  * Guardian feature

## 3. Ideas

* TODO generator based on `# TODO` comments
  * Type (New, Improve, Bug, IDK)
  * Priority (Maybe, Task, Urgent, ASAP)
  * Difficulty (Easy, Hmm, Uhh, WTF)
  * Date (YY-MM-DD)

* Cry in the corner

* DiscordDB
* Asset server
