from loaders.utils.LoaderUtils import *


async def load_events(bot):
    directory = "assets/events"
    cog_type = "L'event"
    total_lines = 16
    total_loaded = 0

    for root, _, files in os.walk(directory):
        if "utils" in root.split(os.sep):
            continue
        total_lines, total_loaded = await load_modules_from_directory(bot, root, files, cog_type, total_lines, total_loaded)

    return total_lines, total_loaded
