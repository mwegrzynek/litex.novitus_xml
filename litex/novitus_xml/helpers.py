import zlib


import lxml.etree as et
import lxml.objectify as obj


def crc32(txt: bytes) -> str:
    return hex(zlib.crc32(txt) & 0xffffffff)[2:].upper()


def etree_to_bytes(root, encoding='cp1250'):
    obj.deannotate(root, cleanup_namespaces=True)
    return et.tostring(
        root,
        encoding=encoding, 
        xml_declaration=False,
        method='xml'
    )


def bytes_to_etree(btes):
    return obj.fromstring(btes)


def assemble_packet(root, crc=False):    
    if crc:
        crc = crc32(etree_to_bytes(root))
        packet = obj.E.packet(root, crc=crc)
    else:
        packet = obj.E.packet(root)

    return packet
    
