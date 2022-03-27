from ipaddress import ip_address
import pyimg4
import plistlib
import getpass
import io
import pyasn1.codec.der.decoder
from rich import print
from fabric import Connection


def main():
    raw_img4 = io.BytesIO()

    print("Welcome to Deverser")
    print("This script will dump blobs from your [bold]jailbroken[/bold] iOS device and copy it to your computer.")
    print("Depending on the blob, you might not be able to use it without a bootROM exploit (e.g. checkm8).")
    print("Refer to https://ios.cfw.guide/saving-blobs/#saving-onboard-blobs for more information.")
    print("")

    while True:
        ip_address = input("Enter the IP address of your device: ")
        if ip_address == "":
            print("Please enter an IP address.")
            continue
        else:
            break
    print("")

    print("Please note that it is normal for the password to [bold]not[/bold] appear.")
    password = getpass.getpass("Enter the root user password (default is 'alpine'): ") or "alpine"
    print("")

    sshport = int(input("Enter the SSH port of your device (default is 22): ") or 22)

    with Connection(ip_address, user="root", port=sshport, connect_kwargs={"password": password}) as c:
        c.run("cat /dev/disk1 | dd of=dump.raw bs=256 count=$((0x4000))")
        c.get("dump.raw", raw_img4)
    
    img4, _ = pyasn1.codec.der.decoder.decode(raw_img4.read())
    im4m = pyimg4.get_im4m_from_img4(img4)
    ecid = pyimg4.get_value_from_im4m(im4m, "ECID")
    with open(f'{str(ecid)}.blob.shsh2', 'wb') as f:
        plistlib.dump(pyimg4.convert_img4_to_shsh(img4), f)
    
    print(f"Done! Your blob has been saved to {str(ecid)}.blob.shsh2")
    

if __name__ == "__main__":
    main()
