'''
Novitus XML Protocol implementation
'''
import logging
import time
import collections


import serial
from lxml.objectify import E


from .helpers import etree_to_bytes, bytes_to_etree, assemble_packet
from .exceptions import CommunicationError, ProtocolError


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Printer:

    def __init__(self, url='hwgrep://.*Novitus.*', timeout=10, encoding='cp1250', crc=True):
        self.url = url
        self.timeout = timeout
        self.encoding = encoding
        self.crc = crc
        self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = serial.serial_for_url(self.url)
            self._conn.timeout = self.timeout
        
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def send_command(self, command, read_reply=False, check_for_errors=False):
        pkt = etree_to_bytes(
            assemble_packet(command, self.crc),
            self.encoding
        )

        log.debug('Sending command: %s', pkt.decode(self.encoding))
        self.conn.write(pkt)

        if read_reply:
            reply = self.conn.read_until(b'</packet>', 5000)

            if not reply:
                raise CommunicationError('No reply from printer')

            log.debug('Received reply: %s', reply.decode(self.encoding))

            reply = bytes_to_etree(reply)
        else:
            reply = None

        if check_for_errors:
            time.sleep(0.1)
            if self.enq()['lastcommanderror'] == 'yes':
                err = self.get_error()
                raise ProtocolError(err)

        return reply

    def dle(self):
        return self.send_command(E.dle(), True).dle.attrib

    def enq(self):
        return self.send_command(E.enq(), True).enq.attrib

    def set_error(self, value):
        cmd = E.error(
            '',
            action='set',
            value=value
        )

        self.send_command(cmd)

    def get_error(self):
        cmd = E.error(
            '',
            action='get',
            value=''
        )

        return int(self.send_command(cmd, True).error.get('value'))

    def invoice_begin(self, **kwargs):

        defined_args = dict(
            invoice_type=('invoice', 'pharmacy'),
            number=None,
            nip=None,
            description=('both', 'original'),
            paymentname=None,
            paymentdate=None,
            recipient=None,
            issuer=None,
            copies=None,
            margins=('yes', 'no'),
            signarea=('yes', 'no'),
            customernameoptions=('info', 'all', 'none'),
            sellernameoptions=('info', 'all', 'none'),
            paidlabel=None,
            selldate=None,
            buyerlabel=None,
            additionalinfo=None
        )

        cmd = E.invoice()

        cmd.set('action', 'begin')

        # Prepare options
        options = set(kwargs.pop('options', []))
        if options:
            for op in options:
                if op in range(1, 20):
                    op_tag = cmd.append(E.option('', id=str(op)))

        # Prepare customer info
        customer = kwargs.pop('customer', [])
        for cust in customer:
            cust_tag = cmd.append(E.customer(cust))

        args = {}
        for name, value in kwargs.items():
            if name not in defined_args:
                raise TypeError('Unknown argument: {}'.format(name))
            
            allowed_values = defined_args.get(name)
            if allowed_values is not None and value not in allowed_values:
                raise TypeError(
                    'Argument {} has wrong value: {} (not in {})'.format(
                        name,
                        value,
                        allowed_values
                    )
                )

            if value is not None:
                cmd.set(name, str(value))

        self.send_command(cmd, check_for_errors=True)

    def invoice_cancel(self):
        cmd = E.invoice('', action='cancel')
        self.send_command(cmd, check_for_errors=True)

    def invoice_close(
        self,
        total,
        systemno,
        checkout,
        cashier,
        buyer
    ):        
        cmd = E.invoice(
            '', 
            action='close',
            total=str(total),
            systemno=systemno,
            checkout=checkout,
            cashier=cashier,
            buyer=buyer
        )
        self.send_command(cmd, check_for_errors=True)

    def item(
        self, 
        name,
        quantity,
        quantityunit,
        ptu,
        price,
        plu='',
        action='sale',
        recipe='',
        charge='',
        description='',
        discount_name='',
        discount_value=None,
        discount_descid=0
    ):
        if discount_value is not None:
            dsc = E.discount(
                '',
                action='discount',
                name=discount_name,
                value=discount_value,
                descid=str(discount_descid)
            )
        else:
            dsc = ''

        cmd = E.item(
            dsc, 
            name=name, 
            quantity=str(quantity),
            quantityunit=quantityunit,
            ptu=ptu,
            price=str(price),
            plu=plu,
            action=action,
            recipe=recipe,
            charge=charge,
            description=description
        )

        self.send_command(cmd, check_for_errors=True)

    def discount(
        self, 
        value,
        name,
        descid
    ):
        cmd = E.discount(
            '', 
            value=value,
            name=name,
            descid=str(descid),
            action='discount'
        )

        self.send_command(cmd, check_for_errors=True)
        
    def markup(
        self, 
        value,
        name,
        descid
    ):
        cmd = E.discount(
            '', 
            value=value,
            name=name,
            descid=str(descid),
            action='markup'
        )

        self.send_command(cmd, check_for_errors=True)

    def payment_add(
        self,
        type_,
        value,
        rate=1,
        mode='payment',
        name=''
    ):
        cmd = E.payment(
            '',
            action='add',
            type=type_,
            value=str(value),
            rate=str(rate),
            mode=mode,
            name=name
        )

        self.send_command(cmd, check_for_errors=True)

    def receipt_begin(
        self, 
        mode='online',
        pharmaceutical='no'        
    ):
        cmd = E.receipt(
            '',
            action='begin',
            mode=mode,
            pharmaceutical=pharmaceutical
        )

        self.send_command(cmd, check_for_errors=True)

    def receipt_cancel(self):        
        cmd = E.receipt('', action='cancel')
        self.send_command(cmd, check_for_errors=True)

    def receipt_close(
        self,   
        total,     
        systemno,
        checkout,
        cashier,        
        charge=None,
        nip=None
    ):        
        cmd = E.receipt(
            '', 
            action='close',
            total=str(total),
            systemno=systemno,
            checkout=checkout,
            cashier=cashier
        )

        if charge is not None:
            cmd.set('charge', str(charge))

        if nip is not None:
            cmd.set('nip', nip)

        self.send_command(cmd, check_for_errors=True)

    def non_fiscal_printout(
        self,   
        lines,  
        systemno='',
        nonfiscalheader='yes'
    ):        
        cmd = E.nonfiscalprintout(
            '',             
            systemno=systemno,
            nonfiscalheader=nonfiscalheader
        )

        for line in lines:
            if isinstance(line, collections.Mapping):
                text = line.pop('text', '')
                
                cmd.append(E.line(
                    text,
                    **line
                ))

            else:
                # Just a text line
                cmd.append(E.line(line))

        self.send_command(cmd, check_for_errors=True)

    def open_drawer(self):

        cmd = E.control(
            '',
            action='drawer'
        )

        self.send_command(cmd, check_for_errors=True)

    def info_checkout(self, type_='receipt'):

        cmd = E.info(
            '',
            action='checkout',
            type=type_,
            isfiscal='?',
            lasterror='?'
        )

        return self.send_command(
            cmd, 
            read_reply=True, 
        ).info

    def taxrates_get(self):

        cmd = E.taxrates(
            '',
            action='get'
        )

        res = self.send_command(
            cmd, 
            read_reply=True, 
        )

        tax_rates = [
            (ptu.get('name'), ptu.text) for ptu in res.taxrates.ptu
        ]

        return tax_rates
        

    

