#!/usr/local/bin/perl
#

use lib '.';
use Geo::WeatherNOAA;

$CITY = "NEW YORK";
$STATE = "NY";

print get_currentWX_html($CITY,$STATE);
print_forecast($CITY,$STATE);

