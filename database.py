import sqlite3
from typing import List, Dict, Optional


# Connexion à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect('bot_db.sqlite', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


# Initialisation de la base de données
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table pour les groupes cibles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT UNIQUE NOT NULL
        )
    ''')

    # Table pour les utilisateurs autorisés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')

    # Table pour les messages relayés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relayed_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_chat_id TEXT NOT NULL,
            original_message_id TEXT NOT NULL,
            relayed_chat_id TEXT NOT NULL,
            relayed_message_id TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Gestion des groupes
def add_group(group_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO groups (group_id) VALUES (?)', (group_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Groupe déjà existant
    finally:
        conn.close()


def remove_group(group_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM groups WHERE group_id = ?', (group_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def list_groups() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT group_id FROM groups')
    groups = [row['group_id'] for row in cursor.fetchall()]
    conn.close()
    return groups


# Gestion des utilisateurs
def add_user(username: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Utilisateur déjà existant
    finally:
        conn.close()


def remove_user(username: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def list_users() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    users = [row['username'] for row in cursor.fetchall()]
    conn.close()
    return users


# Gestion des messages relayés
def add_relayed_message(original_chat_id: str, original_message_id: str, relayed_chat_id: str,
                        relayed_message_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO relayed_messages (original_chat_id, original_message_id, relayed_chat_id, relayed_message_id)
            VALUES (?, ?, ?, ?)
        ''', (original_chat_id, original_message_id, relayed_chat_id, relayed_message_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # En cas de duplication
    finally:
        conn.close()


def get_relayed_messages(original_chat_id: str, original_message_id: str) -> List[Dict[str, str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT relayed_chat_id, relayed_message_id
        FROM relayed_messages
        WHERE original_chat_id = ? AND original_message_id = ?
    ''', (original_chat_id, original_message_id))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages


def delete_relayed_message(original_chat_id: str, original_message_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM relayed_messages
        WHERE original_chat_id = ? AND original_message_id = ?
    ''', (original_chat_id, original_message_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0