from datetime import datetime
import pytz


def log_command_usage(bot, user_id, username, command_name):
    try:
        paris_tz = pytz.timezone("Europe/Paris")
        now = datetime.now(paris_tz)

        db = bot.db
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO logs_commandes (user_id, username, commande, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, username, command_name, now)
        )
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"[Logger DB] Erreur lors de l'enregistrement : {e}")
