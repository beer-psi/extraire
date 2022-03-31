import binascii
import pyasn1.codec.der.decoder
import pyasn1.codec.der.encoder
import pyasn1.type.univ
from typing import Union, Any
from rich import print


__all__ = ["IMG4", "IM4R", "IM4M"]


def __remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def endian_converter(val: Union[bytes, str, pyasn1.type.univ.OctetString]) -> str:
    """Converts big endian to small endian and vice versa
    Args:
        val (Union[bytes, str]): Bytes or a hex string to convert
    Returns:
        str: A 0x prefixed hex string
    """
    ba = bytearray()
    if isinstance(val, str):
        ba = bytearray.fromhex(__remove_prefix(val, "0x"))
    else:
        ba = bytearray(val)
    ba.reverse()
    s = "".join(format(x, "02x") for x in ba)
    return f"0x{s}"


class IM4R:
    def __init__(self, im4r: pyasn1.type.univ.Sequence):
        self.im4r = im4r

    @property
    def bncn(self) -> pyasn1.type.univ.Sequence:
        bncn = self.im4r[-1][-1]
        assert str(bncn[0]) == "BNCN"
        assert isinstance(bncn, pyasn1.type.univ.Sequence)
        return bncn


class MANP:
    def __init__(self, manp: pyasn1.type.univ.Sequence):
        assert (manp[0]) == "MANP"
        self._manp = manp

    def __getitem__(self, key: str) -> Any:
        for i in range(len(self._manp[1])):
            if str(self._manp[1][i][0]) == key:
                return self._manp[1][i][1]
        raise KeyError


class IM4M:
    def __init__(self, im4m: pyasn1.type.univ.Sequence):
        self.im4m = im4m
        assert str(self.im4m[0]) == "IM4M"
        assert isinstance(self.im4m, pyasn1.type.univ.Sequence)

        self.im4m_version = im4m[1]
        self.set = im4m[2]
        self.manbpriv = self.set[0]
        assert str(self.manbpriv[0]) == "MANB"

        self.manbset = self.manbpriv[1]
        self.manp = MANP(self.manbset[0])

    def __board_matches_build_identity(self, build_identity: dict) -> bool:
        __dict = {
            "BORD": "ApBoardID",
            "CHIP": "ApChipID",
            "SDOM": "ApSecurityDomain",
        }
        for key, value in __dict.items():
            if int(self.manp[key]) != int(build_identity[value], 16):
                return False
        return True

    def matches_build_identity(self, build_identity: dict) -> bool:
        print("Checking if board matches BuildIdentity... ", end="")
        if not self.__board_matches_build_identity(build_identity):
            print("[red]NO[/red]")
            return False
        print("[green]YES[/green]")

        hash_dict = {}
        for item in self.manbset[1:]:
            tagtype = item[0]
            tagset = item[1]
            for i in range(len(tagset)):
                item2 = tagset[i]
                dgst = binascii.hexlify(bytes(item2[1])).decode()
                hash_dict[dgst] = str(tagtype)

        for key, value in build_identity["Manifest"].items():
            trusted = value.get("Trusted")
            if trusted is not None and not trusted:
                print(f"[green][bold]{key}[/bold]: OK (untrusted)[/green]")
                continue  # OK (untrusted)

            dgst = value.get("Digest")
            if dgst is None:
                print(f"[bold]{key}[/bold]: IGN (no digest in BuildManifest)")
                continue  # IGN (no digest in BuildManifest)

            dgst_str = binascii.hexlify(dgst).decode()
            if hash_dict.get(dgst_str) is not None:
                print(
                    f"[green][bold]{key}[/bold]: OK (found {hash_dict.get(dgst_str)} with matching hash)[/green]"
                )
                continue  # OK (found something with matching hash)
            else:
                if not trusted:
                    print(
                        f"[bold]{key}[/bold]: IGN (hash not found in im4m, but ignoring since not explicitly enforced by the Trusted=YES flag)"
                    )
                    continue
                else:
                    print(
                        f"[red][bold]{key}[/bold]: BAD! (hash not found in im4m)[/red]"
                    )
                    return False  # BAD (hash not found in im4m)
        return True


class IMG4:
    def __init__(self, img4: pyasn1.type.univ.Sequence):
        self.img4 = img4

    @property
    def im4m(self) -> pyasn1.type.univ.Sequence:
        im4m = self.img4[2]
        assert str(im4m[0]) == "IM4M"
        assert isinstance(im4m, pyasn1.type.univ.Sequence)
        return IM4M(im4m)

    @property
    def im4r(self) -> pyasn1.type.univ.Sequence:
        im4r = self.img4[3]
        assert str(im4r[0]) == "IM4R"
        assert isinstance(im4r, pyasn1.type.univ.Sequence)
        return IM4R(im4r)

    def to_shsh(self) -> dict:
        generator = endian_converter(self.im4r.bncn[-1])

        _im4m = self.im4m.im4m
        _im4m.tagSet._TagSet__superTags = (_im4m.tagSet._TagSet__superTags[0],)

        _shsh = {}
        _shsh["ApImg4Ticket"] = pyasn1.codec.der.encoder.encode(_im4m)
        _shsh["generator"] = generator

        return _shsh
