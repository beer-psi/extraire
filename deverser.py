import pyimg4
import plistlib
import getpass
import io
import pyasn1.codec.der.decoder
from rich import print
from fabric import Connection
from typing import Tuple


def interactive_input() -> Tuple[str, str, int]:
    print("Welcome to Deverser")
    print("This script will dump blobs from your [bold]jailbroken[/bold] iOS device and copy it to your computer.")
    print("Depending on the blob, you might not be able to use it without a bootROM exploit (e.g. checkm8).")
    print("Refer to https://ios.cfw.guide/saving-blobs/#saving-onboard-blobs for more information.")
    print("")

    while True:
        device_addr = input("Enter the IP address of your device: ")
        if device_addr == "":
            print("Please enter an IP address.")
            continue
        else:
            break
    print("")

    print("Please note that it is normal for the password to [bold]not[/bold] appear.")
    password = getpass.getpass("Enter the root user password (default is 'alpine'): ") or "alpine"
    print("")

    sshport = int(input("Enter the SSH port of your device (default is 22): ") or 22)
    return (device_addr, password, sshport)


def main():
    device_addr, password, sshport = interactive_input()

    raw_img4 = io.BytesIO()
    with Connection(device_addr, user="root", port=sshport, connect_kwargs={"password": password}) as c:
        c.run("cat /dev/disk1 | dd of=dump.raw bs=256 count=$((0x4000))")
        c.get("dump.raw", raw_img4)  
    img4, _ = pyasn1.codec.der.decoder.decode(raw_img4.read())
    raw_img4.close()

    im4m = pyimg4.get_im4m_from_img4(img4)
    ecid = pyimg4.get_value_from_im4m(im4m, "ECID")
    with open(f'{str(ecid)}.blob.shsh2', 'wb') as f:
        plistlib.dump(pyimg4.convert_img4_to_shsh(img4), f)
    
    print(f"[green]Done! Your blob has been saved to {str(ecid)}.blob.shsh2[/green]")
    if 0x8020 <= int(pyimg4.get_value_from_im4m(im4m, "CHIP")) < 0x8900:
        print("[yellow]Note: Your device is probably an A12+ device.[/yellow]")
        print("[yellow]If you updated to your current version using the Settings app over-the-air, you cannot use this blob, even with a jailbreak[/yellow]")
        print("[yellow]Refer to https://ios.cfw.guide/saving-blobs/#ota-onboard-blobs for more information.[/yellow]")
        print("[yellow]Determine your blob type with https://verify.shsh.host or https://tsssaver.1conan.com/check or img4tool.[/yellow]")


if __name__ == "__main__":
    main()
