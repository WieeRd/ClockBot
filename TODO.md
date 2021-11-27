# WieeRd's TODO note

## 0. Priority Tasks
1. Game module
2. Dropdown Help command
3. Setup Logging
4. Feedback module
5. QRCode, MagicConch

## 1. New Stuff

### 1.1. New Module
* Game 
    - Chess
    - TicTacToe
    - RockPaperScissor
* Custom
    - create custom command (per server)
    - tag command (R. Danny)
* Portal
    - Link channels using webhook
* Statistic
    - command usage
    - network visualization
        + pyvis is inefficient as hell, gotta code myself

### 1.2. New Command
* Tools
    - QRcode generator
    - Starboard
    - Mute / SelfMute
    - get sticker asset
    - Anti Raid / Spam (R. Danny)
* Pranks
    - MagicConch
    - Mention shield, karma

### 1.3. New Feature
* Help command
    - Dropdown Help command
    - Dump as markdown document (README.md)
    - Send help when mentioned
* Logging
    - seperate stdout/stderr
    - on_error() Handler
* Feedback
    - Update announcement
    - Feedback command
* Converter
    - Time (HH:MM)
    - Guild (fuzzy, mutual)
* Internationalization
    - clockbot.command
        + utilize command.extras
        + different attrs per locale
        + locale decorator
    - get_locale()
        + prefered locale (community guild)
        + `ctx.invoked_with`
        + DB (per guild / user)
* Database
    - Should have used MariaDB tbh
    - NullDB, JsonDB: To continue without DB


## 2. Improvements
* Mention
    - easier expression
* Voice
    - ClockBot.js
        + rewrite voice-related features with discord.js
    - Music
        + voice command
    - TTS
        + kakao speech
        + change voice
        + sound effect
        + voice overlapping
    - stage channel support
* Pranks
    - preserve text objects (mention, emoji, ...)
    - new filters
        + Chaos
        + Mirror (vertical & horizontal)
        + NyanChat
        + Hawawa
    - bonk
        + more variants (kkang, RIP, triggered)
        + support file attachments
* Clock
    - better delay mechanic

## 3. Ideas

* TODO generator based on `# TODO` comments
    - Type (New, Improve, Bug, IDK)
    - Priority (Maybe, Task, Urgent, ASAP)
    - Difficulty (Easy, Hmm, Uhh, WTF)
    - Date (YY-MM-DD)

* Cry in the corner
