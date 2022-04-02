import os
import socket
import tempfile
from typing import Optional, Tuple, Union

import paramiko.ssh_exception
import pyasn1.codec.der.decoder
from fabric import Connection
from rich import print
from rich.prompt import Prompt

from .pyimg4 import IMG4


def introduction():
    print("Welcome to Extraire")
    print(
        "This program will dump blobs from your [bold]jailbroken[/bold] iOS device and "
        "copy it to your computer."
    )
    print(
        "Depending on the blob, you might [bold]not[/bold] be able to use it without a "
        "bootROM exploit (e.g. checkm8)."
    )
    print(
        "Refer to https://ios.cfw.guide/saving-blobs/#saving-onboard-blobs for more "
        "information.",
        end="\n\n",
    )


def interactive_input(
    address: Optional[str] = None,
    password: Optional[str] = None,
    port: Optional[int] = None,
) -> Tuple[str, str, int]:
    if None in (address, password, port) or "" in (address, password, port):
        print(
            "Options given out in [bold blue](blue parentheses)[/bold blue] are "
            "default values and will be used if you haven't specified an option.",
            end="\n\n",
        )

    if not address:
        while True:
            _address = Prompt.ask("[bold]Enter the device's IP address[/bold]")
            if _address == "":
                print("Please enter an IP address.")
                continue
            else:
                break
        [_address, port] = (
            _address.split(":", 2) if ":" in _address else [_address, None]
        )
        print("")

    if not password:
        print(
            "Please note that it is normal for the password to [bold]not[/bold] appear."
        )
        _password = Prompt.ask(
            "[bold]Enter the root user password[/bold]", password=True, default="alpine"
        )
        print("")

    if not port:
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
                c.run("rm -f dump.raw")
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
                f"[red]Please specify the port separately. {address} is not a valid "
                "input.[/red]"
            )
            return False

        with open(rawdump, "rb") as f:
            img4, _ = pyasn1.codec.der.decoder.decode(f.read())
    return IMG4(img4)
