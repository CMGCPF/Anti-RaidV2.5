import os
import importlib.util
from colorama import Fore, Style


def count_file_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)


async def load_modules_from_directory(bot, root, files, cog_type, total_lines, total_loaded):
    for filename in files:
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(root, filename)
            module_display_name = os.path.splitext(os.path.relpath(filepath, os.getcwd()))[0].replace(os.sep, ".")

            try:
                spec = importlib.util.spec_from_file_location(module_display_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "setup"):
                    await module.setup(bot)

                print(
                    f"{Fore.GREEN}{cog_type} : {Style.BRIGHT}{Fore.YELLOW}{module_display_name}{Style.RESET_ALL}"
                    f"{Fore.GREEN} a été activé avec succès !{Style.RESET_ALL}"
                )

                total_lines += count_file_lines(filepath)
                total_loaded += 1

            except Exception as e:
                print(
                    f"{Fore.RED}Erreur lors du chargement de {cog_type} "
                    f"{Style.BRIGHT}{Fore.YELLOW}{module_display_name}{Style.RESET_ALL}"
                    f"{Fore.RED} : {e}{Style.RESET_ALL}"
                )

    return total_lines, total_loaded
