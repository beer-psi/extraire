from sys import exit
from rich import print
from deverser.deverser import main


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[red]Aborted by user.[/red]")
        exit(1)
