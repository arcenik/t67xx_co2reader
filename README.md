## Synopsis

A basic module to read data from Telaire T67xx co2 sensor. Only basic functionnality are implemented.

## Usage example

Here is a simple example

> from t67xx import t67xx
> ser = t67xx()
> print "co2 value is  {val}".format( val=ser.read_co2())

You can specify the device where the sensor is attached

> ser = t67xx()

## License

This is available under [GPL License](http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).


