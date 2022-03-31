from sys import exit
from rich import print
from extraire.extraire import main


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[red]Aborted by user.[/red]")
        exit(1)
