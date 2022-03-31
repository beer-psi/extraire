import argparse
import os
import plistlib
import paramiko.ssh_exception
import pyasn1.codec.der.decoder
import pyasn1.type.univ
import socket
import tempfile
from .pyimg4 import IMG4
from fabric import Connection
from rich import print
from rich.prompt import Prompt
from typing import Optional, Tuple, Union


def interactive_input(
    address: Optional[str] = None,
    password: Optional[str] = None,
    port: Optional[int] = None,
) -> Tuple[str, str, int]:
    print("Welcome to Extraire")
    print(
        "This program will dump blobs from your [bold]jailbroken[/bold] iOS device and copy it to your computer."
    )
    print(
        "Depending on the blob, you might [bold]not[/bold] be able to use it without a bootROM exploit (e.g. checkm8)."
    )
    print(
        "Refer to https://ios.cfw.guide/saving-blobs/#saving-onboard-blobs for more information.",
        end="\n\n",
    )
    if None in (address, password, port):
        print(
            "Options given out in [bold blue](blue parentheses)[/bold blue] are default values and will be used if you haven't specified an option.",
            end="\n\n",
        )

    if address is None:
        while True:
            _address = Prompt.ask("[bold]Enter the device's IP address[/bold]")
            if _address == "":
                print("Please enter an IP address.")
                continue
            else:
                break
        print("")

    if password is None:
        print(
            "Please note that it is normal for the password to [bold]not[/bold] appear."
        )
        _password = Prompt.ask(
            "[bold]Enter the root user password[/bold]", password=True, default="alpine"
        )
        print("")

    if port is None:
        _port = int(Prompt.ask("[bold]Enter the SSH port[/bold]", default="22"))

    return (address or _address, password or _password, port or _port)


def dump_raw_apticket(address: str, password: str, port: int) -> Union[IMG4, bool]:
    with tempfile.TemporaryDirectory() as tmpdir:
        rawdump = os.path.join(tmpdir, "dump.raw")
        try:
            with Connection(
                address,
                user="root",
                port=port,
                connect_kwargs={
                    "password": password,
                },
                connect_timeout=10.0,
            ) as c:
                c.run("dd if=/dev/disk1 of=dump.raw bs=256 count=$((0x4000))")
                c.get("dump.raw", rawdump)
        except paramiko.ssh_exception.NoValidConnectionsError:
            print("[red]Could not connect to device.[/red]")
            return False
        except paramiko.ssh_exception.AuthenticationException:
            print("[red]Could not authenticate with your device.[/red]")
            print("[red]Please check if:[/red]")
            print("[red] - You entered the correct password[/red]")
            print("[red] - You have not disabled root login[/red]")
            return False
        except paramiko.ssh_exception.SSHException:
            print("[red]An SSH2 error occured.[/red]")
            return False
        except socket.timeout:
            print("[red]Timed out trying to connect.[/red]")
            return False
        except OSError as oserr:
            print(f"[red]OSError {oserr.errno} occured: {os.strerror(oserr.errno)}")
            return False
        except ValueError:
            print(
                f"[red]Please specify the port separately. {address} is not a valid input.[/red]"
            )
            return False

        with open(rawdump, "rb") as f:
            img4, _ = pyasn1.codec.der.decoder.decode(f.read())
    return IMG4(img4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host_port", metavar="HOST[:PORT]", nargs="?", help="The device's IP address"
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

    if args.non_interactive:
        if args.host_port is None:
            print(
                "[red]Device IP address not specified, and user asked for non-interactive mode. Exiting.[/red]"
            )
            return 1
        args.password = "alpine" if args.password is None else args.password
    if args.host_port is not None:
        [address, port] = (
            args.host_port.split(":", 2)
            if ":" in args.host_port
            else [args.host_port, 22 if args.non_interactive else None]
        )
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
            "[yellow][bold]Note:[/bold] Your device is probably an A12+ device.[/yellow]"
        )
        print(
            "[yellow]If you updated to your current version using the Settings app over-the-air, you [bold]cannot[/bold] use this blob, even with a jailbreak.[/yellow]"
        )
        print(
            "[yellow]Refer to https://ios.cfw.guide/saving-blobs/#ota-onboard-blobs for more information.[/yellow]"
        )
        print(
            "[yellow]Determine your blob type with https://verify.shsh.host or https://tsssaver.1conan.com/check or img4tool.[/yellow]"
        )
    return 0
