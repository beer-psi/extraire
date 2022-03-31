from pyimg4 import *
import plistlib
import socket
import tempfile
import os
import paramiko.ssh_exception
import pyasn1.codec.der.decoder
import pyasn1.type.univ
from rich import print
from rich.prompt import Prompt
from sys import exit
from fabric import Connection
from typing import Tuple, Union


def interactive_input() -> Tuple[str, str, int]:
    print("Welcome to Deverser")
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
    print(
        "Options given out in [bold blue](blue parentheses)[/bold blue] are default values and will be used if you haven't specified an option.",
        end="\n\n",
    )

    while True:
        device_addr = Prompt.ask("[bold]Enter the device's IP address[/bold]")
        if device_addr == "":
            print("Please enter an IP address.")
            continue
        else:
            break
    print("")

    print("Please note that it is normal for the password to [bold]not[/bold] appear.")
    password = Prompt.ask(
        "[bold]Enter the root user password[/bold]", password=True, default="alpine"
    )
    print("")

    sshport = int(Prompt.ask("[bold]Enter the SSH port[/bold]", default="22"))
    return (device_addr, password, sshport)


def dump_raw_apticket(
    address: str, password: str, port: int
) -> Union[IMG4, bool]:
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
    device_addr, password, sshport = interactive_input()
    img4 = dump_raw_apticket(device_addr, password, sshport)
    if not img4:
        return 1
    ecid = str(img4.im4m["ECID"])
    with open(f"{ecid}.blob.shsh2", "wb") as f:
        plistlib.dump(img4.to_shsh(), f)

    print(f"[green]Done! Your blob has been saved to {ecid}.blob.shsh2[/green]")
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


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[red]Aborted by user.[/red]")
        exit(1)
