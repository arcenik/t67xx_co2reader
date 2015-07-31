
__author__    = "Francois Scala"
__copyright__ = "Copyright 2015"
__license__   = "GPL"
__version__   = "0.1"
__status__    = "Development"

################################################################################
import pprint, sys, time, binascii, logging
import serial

################################################################################
SLAVE_ADDR = chr(0x15)

CMD_REG_READ = chr(0x04)

ADDR_STATUS = "" + chr(0x13) + chr(0x8a)
ADDR_GASPPM = "" + chr(0x13) + chr(0x8b)

REG_STATUS = "" + chr(0x00) + chr(0x01)
REG_GASPPM = "" + chr(0x00) + chr(0x01)

################################################################################
class ts67xxError(Exception):
    pass

################################################################################
class t67xx(object):
    '''
    Basic interface to read data from a Telaire co2 sensor.

    The status flags are :

        STATUS_ERROR
        STATUS_FLASH_ERROR
        STATUS_CALIBRATION_ERROR
        STATUS_RS232
        STATUS_RS485
        STATUS_I2C
        STATUS_WARMUP_MODE
        STATUS_SINGLEPOINT_CALIBRATION

    '''

    STATUS_ERROR = 0x1 << 0
    STATUS_FLASH_ERROR = 0x1 << 1
    STATUS_CALIBRATION_ERROR = 0x1 << 2
    STATUS_RS232 = 0x1 << 8
    STATUS_RS485 = 0x1 << 9
    STATUS_I2C = 0x1 << 10
    STATUS_WARMUP_MODE = 0x1 << 11
    STATUS_SINGLEPOINT_CALIBRATION = 0x1 << 15

    ############################################################################
    def __init__(self, dev="/dev/ttyUSB0"):
        '''
        By default, use the first serial/USB  converter /dev/ttyUSB0
        '''
        # logging
        self.log = logging.getLogger("stream-test01.py")
        #self.log.setLevel(logging.DEBUG)
        self.log.setLevel(logging.WARNING)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s:%(lineno)s [%(levelname)s] %(message)s'))
        self.log.addHandler(handler)

        #
        # open serial port
        #
        self.ser = serial.Serial(port=dev, baudrate=19200, bytesize=8, parity='E', stopbits=1)

        if not self.ser.isOpen():
            self.ser.open()

        if self.ser.isOpen():
            self.log.debug("Serial %s is opened" %(dev))
        else:
            self.log.warning("Serial %s is opened" %(dev))
            sys.exit(1);

    ############################################################################
    def _write(self, data):

        self.ser.write(data)

    ############################################################################
    def _read(self, length):
        return self.ser.read(length)

    ############################################################################
    def _recv(self):

        time.sleep(.1)

        head=self._read(3)
        size=int(binascii.hexlify(head[2]))

        #self.log.debug("="*80)
        #self.log.debug("received header : %s" %(pprint.pformat(head)) )
        #self.log.debug("size : %d "%(size))

        data = self._read(size+2)
        buffer=head + data[:-2]
        crc = (int(binascii.hexlify(data[-1]),16)<<8) + (int(binascii.hexlify(data[-2]),16)<<0)

        self.log.debug( "[_recv] received crc is  0x{val1:02x}{val2:02x}".format(
            val1=int(binascii.hexlify(data[-1]),16),
            val2=int(binascii.hexlify(data[-2]),16)
        ))
        self.log.debug( "[_recv] computed crc is  0x{val:04x}".format(val=self._crc16(buffer)))

        if crc != self._crc16(buffer):
            raise ts67xxError("Received crc is invalid (Crc : 0x{crc:04x}, Data : \"{data}\")".format(
                crc=crc, data=pprint.pformat(head+data)
            ))

        return data

    ############################################################################
    def _crc16(self,bytes):

        crc = 0xffff
        while True:

            if(len(bytes)<= 0):
                break

            char1 = int(binascii.hexlify(bytes[0]),16)
            bytes=bytes[1:]
            crc ^= (char1&0xff) 

            for a in xrange(8):
                if crc&0x1 != 0:
                    crc >>= 1
                    crc ^= 0xa001
                else:
                    crc >>= 1

        return crc

    ############################################################################
    def _req(self, buffer):
        crc = self._crc16(buffer)

        buffer += chr(crc & 0xff )
        buffer += chr((crc & 0xff00) >> 8 )

        #self.log.debug("[_req] computed checksum is : {buf}".format(buf=pprint.pformat(buffer)))
        return self._write(buffer)

    ############################################################################
    def read_status(self):
        '''
        Return the status bit flags integer
        '''
        cmd = SLAVE_ADDR
        cmd += CMD_REG_READ
        cmd += ADDR_STATUS
        cmd += REG_STATUS

        self._req(cmd)
        res=self._recv()

        value = int(binascii.hexlify(res[0]),16)*256 + int(binascii.hexlify(res[1]),16)
        crc = res[2:4]
        
        self.log.debug("=" * 80)
        self.log.debug("received data : %s" %(pprint.pformat(res)))
        self.log.debug("value is %d"%( value))
        self.log.debug("crc is %s"%(pprint.pformat(crc)))

        return value

    ############################################################################
    def read_co2(self):
        '''
        Return the co2 value
        '''

        cmd = SLAVE_ADDR
        cmd += CMD_REG_READ
        cmd += ADDR_GASPPM
        cmd += REG_GASPPM

        self._req(cmd)
        res=self._recv()

        value = int(binascii.hexlify(res[0]),16)*256 + int(binascii.hexlify(res[1]),16)
        crc = res[2:4]
        
        self.log.debug("=" * 80)
        self.log.debug("received data : %s" %(pprint.pformat(res)))
        self.log.debug("value is %d"%( value))
        self.log.debug("crc is %s"%(pprint.pformat(crc)))

        return value



