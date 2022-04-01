import argparse
import plistlib
from sys import exit

from rich import print

from extraire.extraire import dump_raw_apticket, interactive_input, introduction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host_port",
        metavar="HOST[:PORT]",
        nargs="?",
        help="The device's IP address",
        default="",
    )
    parser.add_argument(
        "-p", "--password", help="The device's root user password", required=False
    )
    parser.add_argument(
        "-o", "--output", help="Where to save the dumped blob", required=False
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Don't interactively ask for missing value (assume default if missing)",
        required=False,
    )
    args = parser.parse_args()

    [address, port] = (
        args.host_port.split(":", 2)
        if ":" in args.host_port
        else [args.host_port, 22 if args.non_interactive else None]
    )

    introduction()
    if args.non_interactive:
        if not address:
            print(
                "[red]Device address not specified, and user asked for non-interactive "
                "mode. Exiting.[/red]"
            )
            return 1
        password = args.password or "alpine"
    else:
        address, password, port = interactive_input(address, args.password, port)

    img4 = dump_raw_apticket(address, password, port)
    if not img4:
        return 1

    ecid = str(img4.im4m["ECID"])
    args.output = f"{ecid}.blob.shsh2" if args.output is None else args.output
    with open(args.output, "wb") as f:
        plistlib.dump(img4.to_shsh(), f)

    print(f"[green]Done! Your blob has been saved to {args.output}[/green]")
    if 0x8020 <= int(img4.im4m["CHIP"]) < 0x8900:
        print(
            "[yellow][bold]Note:[/bold] Your device is probably an A12+ device."
            "[/yellow]"
        )
        print(
            "[yellow]If you updated to your current version using the Settings app "
            "over-the-air, you [bold]cannot[/bold] use this blob, even with a "
            "jailbreak.[/yellow]"
        )
        print(
            "[yellow]Refer to https://ios.cfw.guide/saving-blobs/#ota-onboard-blobs "
            "for more information.[/yellow]"
        )
        print(
            "[yellow]Determine your blob type with https://verify.shsh.host or "
            "https://tsssaver.1conan.com/check or img4tool.[/yellow]"
        )
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[red]Aborted by user.[/red]")
        exit(1)
