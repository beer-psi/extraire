from typing import Any, Union

import pyasn1.codec.der.decoder
import pyasn1.codec.der.encoder
import pyasn1.type.univ

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


class IM4M:
    def __init__(self, im4m: pyasn1.type.univ.Sequence):
        self.im4m = im4m

    def __getitem__(self, key: str) -> Any:
        assert str(self.im4m[0]) == "IM4M"
        assert isinstance(self.im4m, pyasn1.type.univ.Sequence)

        set = self.im4m[2]
        manbpriv = set[0]
        assert str(manbpriv[0]) == "MANB"

        manbset = manbpriv[1]
        manppriv = manbset[0]
        assert str(manppriv[0]) == "MANP"

        manp = manppriv[1]

        for i in range(len(manp)):
            if str(manp[i][0]) == key:
                return manp[i][1]

        raise KeyError


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
