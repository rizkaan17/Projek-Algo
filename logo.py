import pyfiglet
from colorama import Fore, init

init(autoreset=True)

logo = pyfiglet.figlet_format("AGROMAME")
print(Fore.GREEN + logo)
