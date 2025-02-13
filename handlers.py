import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    add_group, remove_group, list_groups,
    add_user, remove_user, list_users,
    add_relayed_message, get_relayed_messages, delete_relayed_message
)
from config import ADMIN_USERS

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Vérifie si l'utilisateur est autorisé
def is_authorized(update: Update) -> bool:
    username = update.effective_user.username
    return username in ADMIN_USERS or username in list_users()

# Commandes pour les groupes
async def handle_add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    if not context.args:
        await update.message.reply_text("❌ Utilisation : /add_group <group_id>")
        return

    group_id = context.args[0]
    if add_group(group_id):
        await update.message.reply_text(f"✅ Groupe {group_id} ajouté avec succès.")
    else:
        await update.message.reply_text(f"❌ Le groupe {group_id} existe déjà.")

async def handle_remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    if not context.args:
        await update.message.reply_text("❌ Utilisation : /remove_group <group_id>")
        return

    group_id = context.args[0]
    if remove_group(group_id):
        await update.message.reply_text(f"✅ Groupe {group_id} supprimé avec succès.")
    else:
        await update.message.reply_text(f"❌ Le groupe {group_id} n'existe pas.")

async def handle_list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    groups = list_groups()
    if groups:
        await update.message.reply_text(f"📋 Groupes configurés :\n{', '.join(groups)}")
    else:
        await update.message.reply_text("ℹ️ Aucun groupe configuré.")

# Commandes pour les utilisateurs
async def handle_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    if not context.args:
        await update.message.reply_text("❌ Utilisation : /add_user <username>")
        return

    username = context.args[0].lstrip('@')  # Supprimer le "@" si présent
    if add_user(username):
        await update.message.reply_text(f"✅ Utilisateur {username} ajouté avec succès.")
    else:
        await update.message.reply_text(f"❌ L'utilisateur {username} existe déjà.")

async def handle_remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    if not context.args:
        await update.message.reply_text("❌ Utilisation : /remove_user <username>")
        return

    username = context.args[0].lstrip('@')  # Supprimer le "@" si présent
    if remove_user(username):
        await update.message.reply_text(f"✅ Utilisateur {username} supprimé avec succès.")
    else:
        await update.message.reply_text(f"❌ L'utilisateur {username} n'existe pas.")

async def handle_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser cette commande.")
        return

    users = list_users()
    if users:
        await update.message.reply_text(f"📋 Utilisateurs autorisés :\n{', '.join(users)}")
    else:
        await update.message.reply_text("ℹ️ Aucun utilisateur autorisé.")

# Relai des messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Vérifier si l'utilisateur est autorisé
    if not is_authorized(update):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
        return

    # Récupérer le message et son contenu
    message_text = update.message.text
    original_chat_id = update.message.chat_id
    original_message_id = update.message.message_id

    # Relayer le message vers les groupes cibles
    groups = list_groups()
    for group_id in groups:
        try:
            # Envoyer le message dans le groupe cible
            sent_message = await context.bot.send_message(chat_id=group_id, text=message_text)

            # Enregistrer la correspondance dans la base de données
            add_relayed_message(original_chat_id, original_message_id, group_id, sent_message.message_id)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message dans le groupe {group_id} : {e}")

# Suppression des messages relayés
async def handle_message_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Récupérer les informations du message supprimé
    deleted_message_id = update.message.message_id
    chat_id = update.message.chat_id

    # Récupérer les messages relayés correspondants
    relayed_messages = get_relayed_messages(chat_id, deleted_message_id)

    # Supprimer les messages relayés dans les groupes cibles
    for relayed_message in relayed_messages:
        relayed_chat_id = relayed_message['relayed_chat_id']
        relayed_message_id = relayed_message['relayed_message_id']
        try:
            await context.bot.delete_message(chat_id=relayed_chat_id, message_id=relayed_message_id)
            logger.info(f"Message supprimé dans le groupe {relayed_chat_id} (ID: {relayed_message_id}).")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du message dans le groupe {relayed_chat_id} : {e}")

    # Supprimer l'entrée de la base de données
    delete_relayed_message(chat_id, deleted_message_id)