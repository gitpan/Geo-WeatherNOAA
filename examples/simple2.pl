#!/usr/local/bin/perl
#
# Started 3/3/98 Mark Solomon <msolomon@seva.net>
#

use Geo::WeatherNOAA;

print "I'm using WX v$WX::VERSION\n\n";

print_forecast('BLACKSBURG','VA');
