import json
import os
import mysql.connector
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()


def connect_to_database():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )

        cursor = db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS serveurs (
                serveur_id BIGINT PRIMARY KEY,
                statut BOOLEAN DEFAULT FALSE,
                role_wl TEXT,
                salon_wl TEXT,
                sanction ENUM('warn', 'ban', 'timeout', 'kick') DEFAULT 'warn',
                duree INT,
                user_warn TEXT,
                domaines TEXT,
                user_perm TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs_commandes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                username VARCHAR(255),
                commande VARCHAR(255),
                timestamp DATETIME
            )
        """
        )

        db.commit()

        server_settings_cache = {}
        cursor.execute("SELECT * FROM serveurs")
        for row in cursor.fetchall():
            serveur_id = row[0]
            server_settings_cache[serveur_id] = {
                "statut": row[1],
                "role_wl": row[2],
                "salon_wl": row[3],
                "sanction": row[4],
                "duree": row[5],
                "user_warn": row[6],
                "domaines": row[7],
                "user_perm": row[8]
            }

        cursor.close()
        return db, server_settings_cache

    except mysql.connector.Error as err:
        print(
            f"{Fore.RED}[DB ERREUR]{Style.RESET_ALL} Impossible de se connecter à la base de données : {err}"
        )
        return None, {}


async def save_dirty_configs_to_db(bot):
    cursor = bot.db.cursor()
    dirty_found = False

    for guild_id, config in bot.server_settings_cache.items():
        if config.get("dirty"):
            dirty_found = True
            cursor.execute(
                """
                INSERT INTO serveurs (serveur_id, statut, role_wl, salon_wl, sanction, duree, user_warn, domaines, user_perm)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    statut = VALUES(statut),
                    role_wl = VALUES(role_wl),
                    salon_wl = VALUES(salon_wl),
                    sanction = VALUES(sanction),
                    duree = VALUES(duree),
                    user_warn = VALUES(user_warn),
                    domaines = VALUES(domaines),
                    user_perm = VALUES(user_perm)
                """,
                (
                    guild_id,
                    config["statut"],
                    config["role_wl"],
                    config["salon_wl"],
                    config["sanction"],
                    config["duree"],
                    config["user_warn"],
                    config["domaines"],
                    config["user_perm"]
                ),
            )

            config["dirty"] = False

    if dirty_found:
        bot.db.commit()

    cursor.close()
