import pyasn1.codec.der.decoder
import pyasn1.codec.der.encoder
import pyasn1.type.univ
from typing import Union, Optional


__all__ = ["get_im4m_from_img4", "get_im4r_from_img4", "get_bncn_from_im4r", "get_value_from_im4m", "endian_converter", "convert_img4_to_shsh"]


def __remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def get_im4m_from_img4(img4: pyasn1.type.univ.Sequence) -> pyasn1.type.univ.Sequence:
    im4m = img4[2]
    assert str(im4m[0]) == "IM4M"
    assert isinstance(im4m, pyasn1.type.univ.Sequence)
    return im4m


def get_im4r_from_img4(img4: pyasn1.type.univ.Sequence) -> pyasn1.type.univ.Sequence:
    im4r = img4[3]
    assert str(im4r[0]) == "IM4R"
    assert isinstance(im4r, pyasn1.type.univ.Sequence)
    return im4r


def get_bncn_from_im4r(im4r: pyasn1.type.univ.Sequence) -> pyasn1.type.univ.Sequence:
    bncn = im4r[-1][-1]
    assert str(bncn[0]) == "BNCN"
    assert isinstance(bncn, pyasn1.type.univ.Sequence)
    return bncn


def get_value_from_im4m(im4m: pyasn1.type.univ.Sequence, key: str) -> Optional[bytes]:
    """Gets the value of a key from an im4m

    Args:
        im4m (pyasn1.type.univ.Sequence): A decoded im4m.
        key (str): The key to get the value for.
    Returns:
        Union[bytes, NoneType]: The value of the key, or None if the key is not found.
    """
    assert str(im4m[0]) == "IM4M"
    assert isinstance(im4m, pyasn1.type.univ.Sequence)

    set = im4m[2]
    manbpriv = set[0]
    assert str(manbpriv[0]) == "MANB"

    manbset = manbpriv[1]
    manppriv = manbset[0]
    assert str(manppriv[0]) == "MANP"

    manp = manppriv[1]

    for i in range(len(manp)):
        if str(manp[i][0]) == key:
            return manp[i][1]

    return None


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
    s = ''.join(format(x, '02x') for x in ba)
    return f'0x{s}'


def convert_img4_to_shsh(img4: pyasn1.type.univ.Sequence) -> dict:
    """Converts an img4 to an SHSH blob

    Args:
        img4 (pyasn1.type.univ.Sequence): A decoded img4.
    Returns:
        dict: A dictionary containing the SHSH blob, which can be saved to a file with plistlib.
    """
    im4r = get_im4r_from_img4(img4)
    bncn = get_bncn_from_im4r(im4r)
    generator = endian_converter(bncn[-1])

    im4m = get_im4m_from_img4(img4)
    im4m.tagSet._TagSet__superTags = (im4m.tagSet._TagSet__superTags[0],)

    shsh = {}
    shsh["ApImg4Ticket"] = pyasn1.codec.der.encoder.encode(im4m)
    shsh["generator"] = generator

    return shsh
