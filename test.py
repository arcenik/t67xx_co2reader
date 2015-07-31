#! /usr/bin/env python2.7
################################################################################
from t67xx import t67xx

################################################################################
if __name__ == "__main__":
    main()

    ser = t67xx()

    print "status is {val:016b}".format( val=ser.read_status())
    print "co2 value is  {val}".format( val=ser.read_co2())


