# Birthday Ghoul
When it is someone's birthday, they are declared The Birthday Ghoul, being
given a special role.
## Setup
- Pick a directory name. As an example, I will be using `birthdays`.
- Get your bot's token. Here it will be replaced with `bot-token`.
```sh
git clone https://github.com/BeanRob/bg.git
cd bg
echo "dir = '$(pwd)'" > config.py
echo "token = 'bot-token'" >> config.py
cp birthday.service /etc/systemd/system/
systemctl start birthday
```
## Commands
- `/init [channel] [role]`
    - Sets the bot to post messages in `[channel]` and give The Birthday Ghoul
      `[role]`.
- `/addbirth [day] [month]`
    - Registers your birthday.
- `/check`
    - Manually checks for birthdays.
    - Primary use is for if someone adds their birthday on their birthday.
## Miscellany
This is my first time making a Discord bot. If my code is trash, tell me.
