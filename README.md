# litex.novitus_xml
## Driver for a Polish fiscal printer with Novitus XML protocol

**Fiscal printer** is a [fiscal memory device](https://en.wikipedia.org/wiki/Fiscal_memory_device) used to record retail sales in Poland and few other countries in the world (eg. Russia, Czechia).

This library implements parts of [XML protocol](https://www.novitus.pl/sites/default/files/dla-programistow/drukarki-fiskalne/communication_protocol_xml_eng._17.07.2019.pdf) of one of the major Polish manufacturers [Novitus](https://www.novitus.pl/).

Printing receipt example (for more, see tests):

```python
from litex.novitus_xml import Printer

# uses USB device autodetection and no checksumming by default
# for more url examples, see PySerial documentation
# https://pyserial.readthedocs.io/en/latest/url_handlers.html
printer = Printer(
    url='hwgrep://.*Novitus.*'
) 

printer.receipt_begin()

printer.item(
    name='First product',
    quantity=2,
    quantityunit='pcs',
    ptu='A',
    price=4
)

printer.item(
    name='Second product',
    quantity=4,
    quantityunit='pcs',
    description='A long description',
    ptu='A',
    price=2        
)

printer.receipt_close(
    total=16.0,
    systemno='1/TEST/2020',
    checkout='10',
    cashier='John Doe'
)
```