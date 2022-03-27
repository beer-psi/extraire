import pyimg4
import plistlib
import paramiko.ssh_exception
import pyasn1.codec.der.decoder
import socket
import tempfile
import os.path
from rich import print
from rich.prompt import Prompt
from os import remove
from sys import exit
from fabric import Connection
from typing import Tuple


def interactive_input() -> Tuple[str, str, int]:
    print(
        """Welcome to Deverser

This script will dump blobs from your [bold]jailbroken[/bold] iOS device and copy it to your computer.
Depending on the blob, you might [bold]not[/bold] be able to use it without a bootROM exploit (e.g. checkm8).
Refer to https://ios.cfw.guide/saving-blobs/#saving-onboard-blobs for more information.""",
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


def main():
    device_addr, password, sshport = interactive_input()

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with Connection(
                device_addr,
                user="root",
                port=sshport,
                connect_kwargs={
                    "password": password,
                    "timeout": 10.0,
                },
            ) as c:
                c.run("dd if=/dev/disk1 of=dump.raw bs=256 count=$((0x4000))")
                c.get("dump.raw", os.path.join(tmpdir, "dump.raw"))
        except paramiko.ssh_exception.NoValidConnectionsError:
            print("[red]Could not connect to device.[/red]")
            return 1
        except paramiko.ssh_exception.AuthenticationException:
            print("[red]Could not authenticate with your device.[/red]")
            print("[red]Please check if:[/red]")
            print("[red] - You entered the correct password[/red]")
            print("[red] - You have not disabled root login[/red]")
            return 1
        except paramiko.ssh_exception.SSHException:
            print("[red]An SSH2 error occured.[/red]")
            return 1
        except socket.timeout:
            print("[red]Timed out trying to connect.[/red]")
            return 1

        with open("dump.raw", "rb") as f:
            img4, _ = pyasn1.codec.der.decoder.decode(f.read())

    im4m = pyimg4.get_im4m_from_img4(img4)
    ecid = pyimg4.get_value_from_im4m(im4m, "ECID")
    with open(f"{str(ecid)}.blob.shsh2", "wb") as f:
        plistlib.dump(pyimg4.convert_img4_to_shsh(img4), f)

    print(f"[green]Done! Your blob has been saved to {str(ecid)}.blob.shsh2[/green]")
    if 0x8020 <= int(pyimg4.get_value_from_im4m(im4m, "CHIP")) < 0x8900:
        print("[yellow]Note: Your device is probably an A12+ device.[/yellow]")
        print(
            "[yellow]If you updated to your current version using the Settings app over-the-air, you cannot use this blob, even with a jailbreak[/yellow]"
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
