import pyfiglet

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    class _CFallback:
        def __getattr__(self, name):
            return ""
    Fore = Style = _CFallback()

ascii_art = pyfiglet.figlet_format("AGROMAME", font="big_money-ne", width=100, justify="center")
print(Fore.GREEN + ascii_art)