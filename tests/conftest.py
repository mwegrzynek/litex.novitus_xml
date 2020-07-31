import os


from pytest import fixture


@fixture
def printer():
    from litex.novitus_xml import Printer

    return Printer(
        os.environ.get('NOVITUS_URL', 'hwgrep://.*Novitus.*'),
        crc=True
    )
