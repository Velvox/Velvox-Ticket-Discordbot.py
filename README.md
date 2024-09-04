# Velvox Discord ticket bot

A simple Discord ticket bot with simple commands that don't require much user input to work.

## Features

- **Automated database setup** with the command `/setupticketdatabase` it will setup the database.
- **All on Discord** This bot doesn't work with a webpanel and works fully with discord slash commands.

## Setup Instructions

### Using Velvox Gamehosting

1. **Download the Bot Package**

   Download the `.tar` package of the bot from the [releases page](https://github.com/Velvox/Velvox-Ticket-Discordbot.py/releases) or import it in to the server.

2. **Upload the Package to Velvox Gamehosting**

    - Buy your [bot (Discord bot.py)](https://billing.velvox.net/index.php/store/discord-bot) and use "Python Generic"
    - Then go to the [gamepanel](https://game.velvox.net) and go to "your server" > files and drop the .tar file in to the `/home/container/` directory, and extract it.
    - Create a database in the "Database" tab and write the login information down.

3. **Configure the Bot**

   - Open the `bot.py` and set the variables and put the correct login data in to the file.
   - Get you bot token here: [Discord Developer Portal](https://discord.com/developers).
     ```python
            DISCORD_TOKEN = 'yourdiscordtoken' # Set your bot token
            DB_HOST = 'yourdatabasehost' # MySQL server IP
            DB_USER = 'yourdatabaseuser' # MySQL user
            DB_PASSWORD = 'yourdatabasepassword' # MySQL password
            DB_NAME = 'yourdatabasename' # MySQL database name
     ```
    - Setup the database with the command `/setupticketdatabase`


4. **Install Required Packages**

   - By default the panel should install the default and neccasary packages. If you get any errors contact [support](https://billing.velvox.net/submitticket.php).

5. **Run the Bot**

   - If you configured your bot the right way when you click "Start" in the gamepanel it should start and you can start using your bot!

## Commands

#### 1. Set ticket category

- `/ticketscategory` Set the ticket category to put the tickets.

#### 2. Setup the database

- `/setupticketdatabase` Adds the needed database tables to make the bot function.

#### 3. Launch the embed

- `/ticketlaunch` Launch the bot so everyone can make a ticket

#### 4. Set or remove ticket role

- `/setrole` Set the role that answers to the ticket (doing this via the ticket category could be better).
- `/removerole` Remove the role that manages the tickets.

#### 5. Add and remove a user of the ticket

- `/adduser` Add a user to the ticket.
- `/removeuser` Remove a user from the ticket.

## License

This bot is licensed under the [GNU General Public License v3.0](https://github.com/Velvox/Velvox-Ticket-Discordbot.py/blob/main/LICENSE). See the `LICENSE` file for more details.
