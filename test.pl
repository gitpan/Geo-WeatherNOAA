# Before `make install' is performed this script should be runnable with
# `make test'. After `make install' it should work as `perl test.pl'

######################### We start with some black magic to print on failure.

# Change 1..1 below to 1..last_test_to_print .
# (It may become useful if the test is moved to ./t subdirectory.)

BEGIN { $| = 1; print "1..5\n"; }
END {print "not ok 1\n" unless $loaded;}
use Geo::WeatherNOAA;
$loaded = 1;
print "ok 1\n";

######################### End of black magic.

# Insert your test code below (better if it prints "ok 13"
# (correspondingly "not ok 13") depending on the success of chunk 13
# of the test code):

my $test = 2;
my $TMPDIR = 'tmp-wxdata-test/';

{
	# Test plain get_forecast() without using cache
	my %wx;
	print "$test...";
	if ( %wx = get_forecast('BOSTON','MA') ) {
		print "ok $test\n";
	} else {
		print "not ok $test\n";
	}
	$test++;
}
{
	# Test get_forecast() using cache
	my %wx;
	if ( %wx = get_forecast('BOSTON','MA',1,$TMPDIR) ) {
		if ( %wx = get_forecast('BOSTON','MA',1,$TMPDIR) ) {
			print "ok $test\n";
		} 
		else {
			print "not ok $test\n";
		}
	}
	else {
		print "not ok $test\n";
	}
	$test++;
}

# We'll now assume that the cache function works

{
	# Test get_currentWX()
	my %wx;
	if ( %wx = get_currentWX('BOSTON','MA') ) {
		print "ok $test\n";
	} 
	else {
		print "not ok $test\n";
	}
	$test++;
}
{
	# Test get_currentWX_html()
	my %wx;
	if ( $wx = get_currentWX_html('BOSTON','MA') ) {
		print "ok $test\n";
	} else {
		print "not ok $test\n";
	}
	$test++;
}
print "You'll want to delete the directory '$TMPDIR'\n";
print "Test complete.\n";

