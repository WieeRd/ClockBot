# WieeRd's TODO note

## 1. New Stuff

### 1.1. New Module
* cogs.game 
    - Chess
    - TicTacToe
    - RockPaperScissor
* cogs.custom
    - create custom command (per server)
    - tag command (R. Danny)
* cogs.portal
    - Link channels using webhook
* cogs.help
    - reload HelpCommand in runtime
* cogs.statistic
    - command usage
    - network visualization
        + pyvis is inefficient as hell, gotta code myself

### 1.2. New Command
* cogs.tools
    - SelfMute
    - Anti Raid / Spam (R. Danny)
    - QRcode generator
    - Starboard
    - get sticker asset
* cogs.pranks
    - MagicConch
    - Mention shield, karma

### 1.3. New Feature
* Help command
    - Dropdown Help command
    - Send help when mentioned
* Logging
    - seperate stdout/stderr
    - on_error() Handler
* Converter
    - Time (HH:MM)
    - Guild (fuzzy, mutual)
* internationalization
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
* cogs.mention
    - easier expression
* cogs.voice
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
* cogs.pranks
    - preserve text objects (mention, emoji, ...)
    - new filters
        + Chaos
        + Mirror (vertical & horizontal)
        + NyanChat
        + Hawawa
    - bonk
        + more variants (kkang, RIP, triggered)
        + support file attachments
* cogs.clock
    - better delay mechanic
