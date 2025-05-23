from loaders.utils.LoaderUtils import *


async def load_commands(bot):
    directory = "assets/commands"
    cog_type = "La commande"
    total_lines = 144
    total_loaded = 0

    groups_path = os.path.join(directory, "groups")
    utils_path = os.path.abspath(os.path.join(directory, "utils"))

    if os.path.exists(groups_path):
        for root, _, files in os.walk(groups_path):
            total_lines, total_loaded = await load_modules_from_directory(bot, root, files, cog_type, total_lines, total_loaded)

    for root, _, files in os.walk(directory):
        abs_root = os.path.abspath(root)

        if abs_root.startswith(os.path.abspath(groups_path)) or abs_root.startswith(utils_path):
            continue

        total_lines, total_loaded = await load_modules_from_directory(bot, root, files, cog_type, total_lines, total_loaded)

    return total_lines, total_loaded
