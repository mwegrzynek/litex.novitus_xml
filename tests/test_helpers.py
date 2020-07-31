from lxml.objectify import E


from litex.novitus_xml import crc32, etree_to_bytes, bytes_to_etree, assemble_packet


def test_crc32():    
    assert crc32(
        '\r\n  <informacja akcja="transakcja"/>\r\n'.encode('cp1250')
    ) == '67D858E7'


def test_etree_to_bytes():
    assert etree_to_bytes(E.dle()) == b'<dle/>'


def test_bytes_to_etree():
    assert etree_to_bytes(bytes_to_etree(b'<dle/>')) == b'<dle/>'


def test_assemble_packet_crc():
    assert etree_to_bytes(
        assemble_packet(E.dle(), True)
    ) == b'<packet crc="4259D34E"><dle/></packet>'


def test_assemble_packet_no_crc():
    assert etree_to_bytes(
        assemble_packet(E.dle())
    ) == b'<packet><dle/></packet>'