# bot.py

import logging
import asyncio
import nest_asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import (
    handle_add_group, handle_remove_group, handle_list_groups,
    handle_add_user, handle_remove_user, handle_list_users, handle_message
)
from config import BOT_TOKEN
from database import init_db

# Activer nest_asyncio
nest_asyncio.apply()

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialisation de la base de données
init_db()

# Fonction principale
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Commandes
    application.add_handler(CommandHandler("add_group", handle_add_group))
    application.add_handler(CommandHandler("remove_group", handle_remove_group))
    application.add_handler(CommandHandler("list_groups", handle_list_groups))
    application.add_handler(CommandHandler("add_user", handle_add_user))
    application.add_handler(CommandHandler("remove_user", handle_remove_user))
    application.add_handler(CommandHandler("list_users", handle_list_users))

    # Relai des messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Démarrage du bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())