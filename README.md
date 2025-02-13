# Telegram-relayBot
It's a bot that relays your messages from one main group to another. it must be an administrator of the main group to be able to read the message to be relayed. it is possible to add administrators to the bot, to limit those who want to use the bot.

 - Adding/deleting groups :
 - Command /add_group to add a target group.
 - Command /remove_group to remove a target group.
 - View configured groups:
 - Command /list_groups to display all currently configured target groups.

 - Possibility of defining a list of users authorized to manage the bot.
 - Commands :
 - /add_user to add a user to the whitelist.
 - /remove_user to remove an authorized user.
 - /list_users to display the list of authorized users.

you need to provide your bot token, the admin and group id in config.py file
after running the bot you'll be able to add users directly in th bot, no need to modify the file
don't forget to install the requirements modules
