#!/usr/local/bin/perl -T
#
#	Get local Wx data from http://iwin.nws.noaa.gov/iwin/va/zone.html,
#	find the local zone, and place this data in a file.
#
#	3/2/98 Mark Solomon <msolomon@seva.net>
#	Copyright 1998 Mark Solomon (See GNU GPL)
#	$Id: wx.cgi,v 3.4 1998/03/15 21:40:03 msolomon Exp msolomon $
#	$Name:  $
#

use lib '.';
use Geo::WeatherNOAA;
use CGI;

BEGIN {
	$ENV{PATH} = '/usr/bin:/bin';
	$ENV{CDPATH} = '';
}


my $VERSION = do { my @r = (q$Revision: 3.4 $ =~ /\d+/g); sprintf "%d."."%02d" x $#r, @r };
my $ME = ( split('/',$0) )[-1] . " $VERSION";

my $q = new CGI;

my $city = uc($q->param("city")) || 'NEWPORT NEWS';
my $state = uc($q->param('state')) || 'VA';
Geo::WeatherNOAA::First_caps($city);

($state) = ($state =~ /^(\w\w)/);
my @states = Geo::WeatherNOAA::states();

if (! grep /^\L$state$/, @states) {
	print "Content-type:text/plain\n\n";
	print "ERROR: $state is not a state\n";
	exit(1);
}
elsif ( lc($state) eq 'va') {
}
elsif ( ! $q->param(REDIR) ) {
	my $MyURL = 'http://www.seva.net/~msolomon/wx/wx.cgi';
	my $mycity = $city;
	$mycity =~ tr/ /+/d;
	$MyURL .= "?city=$mycity&state=$state&REDIR=1";
	print "Content-type:text/html\n\n";
	print '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">';
	print "<HTML><HEAD><TITLE>Mark's Local Wx</TITLE>\n";
	print "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=$MyURL\">\n";
	print "<BODY BGCOLOR='#e5e5e5'>\n";
	print "<H2>Please wait, collecting weather data from NOAA</H2>\n";
	print "Although this server caches weather for the state of Virginia automatically, other states' data needs to be retreived.\n";
	print "<HR WIDTH='75%'>\nIf your browser is not currently trying to load the weather data page, <A HREF=\"$MyURL\">try this link.</A>\n";
	print "<HR WIDTH='75%'>\n<CENTER><FONT SIZE=2><I>Copyright &copy; 1998 Mark Solomon</I></FONT></CENTER>\n";
	print "</BODY>\n</HTML>\n";
	exit(0);
}


	my $GREY	= '#E2E2E5';
	my $DARKGREY	= '#C2C2C5';
	my $RED		= '#FF8389';
	my $DARKRED	= '#440000';
	my $DARKBLUE	= '#37476F';
	my $MEDBLUE	= '#96A7D3';
	my $GREYBLUE	= '#a2a2c5';
	my $LIGHTBLUE	= '#B6C7F3';
	my $LIGHT 	= "BGCOLOR=\"$LIGHTBLUE\"";
	my $LIGHTTEXT 	= "COLOR=\"#333333\"";
	my $MEDIUM 	= "BGCOLOR=\"$MEDBLUE\"";
	my $MEDIUMTEXT 	= "COLOR=\"#17274F\"";
	my $DARK 	= "BGCOLOR=\"$GREY\"";
	my $DARKTEXT 	= "COLOR=\"$DARKBLUE\"";

my $out;

#$| = 1;
#print "Content-Type: multipart/x-mixed-replace;boundary=myboundary\n\nmyboundary\n";
#print $q->start_html(-title=>"Mark's Local Wx for $city, $state",-bgcolor=>'#e5e5e5');
#print "<H2>Please wait...collecting data</H2>\n\nmyboundary";

%wx = get_forecast($city,$state,30);

$out = $q->header,"\n";
$out .= $q->start_html(-title=>"Mark's Local Wx for $city, $state",-bgcolor=>'#e5e5e5');
$out .=<<ENDTOP;
<FONT SIZE=1>According to <A HREF='http://www.noaa.gov'>NOAA</A>:</FONT>
<P>
<CENTER>
<TABLE WIDTH=550 CELLPADDING=2 CELLSPACING=1 BORDER=0 BGCOLOR='#000000'><TR><TD>
<TABLE WIDTH=550 CELLPADDING=5 CELLSPACING=1 BORDER=0 BGCOLOR='#000000'>

<!-- Title bar -->
<TR>
	<TD $MEDIUM VALIGN=BOTTOM><FONT $DARKTEXT SIZE=2>Day</TD>
	<TD $MEDIUM><FONT $MEDIUMTEXT SIZE='+1'>Wx for $city, $state</FONT></TD>
</TR>
ENDTOP
$out .= "<TR>\n\t<TD $LIGHT VALIGN=TOP><FONT $DARKTEXT>Currently</TD>\n";
$out .= "\t<TD BGCOLOR=\"$GREY\"><FONT $LIGHTTEXT>";
$out .= get_currentWX_html($city,$state,30);
$out .= "</FONT></TD>\n</TR>\n";

sub run_list {
	my ($list,$title) = @_;
	return if ! $#$list eq 0;
	
	if ($title) {
		$out .= "<TR><!-- Separator/title -->\n";
		# $out .= "<TD $LIGHT>&nbsp;</TD>\n";
		$out .= "<TD COLSPAN=2 ALIGN=CENTER BGCOLOR=\"$DARKGREY\" VALIGN=BOTTOM><FONT $LIGHTTEXT SIZE=2>$title</TD></TR>\n";
	}
	foreach $item (@$list) {
		my ($day,$data) = split(':',$item);
		$day or $day = '&nbsp;';
		$data =~ tr/\r\n//d;
		$data =~ s/^\s$//;
		if ($data) {
			$out .= "<TR>\n\t<TD $LIGHT VALIGN=TOP><FONT $DARKTEXT>$day</TD>\n";
	        	$out .= "\t<TD BGCOLOR=\"$GREY\"><FONT $LIGHTTEXT>$data</FONT></TD>\n</TR>\n";
		}
		else {
	        	$out .= "<TR>\n\t<TD BGCOLOR=\"$RED\" COLSPAN=2 ALIGN=CENTER>";
			$out .= "<FONT COLOR=\"$DARKRED\">$day</TD>\n</TR>\n";
		}	
	}
} # run_list()

@NEAR = split "\n", $wx{NEAR};
@EXTENDED = split "\n", $wx{EXTENDED};
run_list('NEAR',"Forecast: <FONT SIZE=\"-2\">(Updated $wx{Date})</FONT>") if (@NEAR);
run_list('EXTENDED','Extended Forecast:') if (@EXTENDED);
$wx{Coverage} ||= 'No data available for area requested';

$out .= <<ENDBOTTOM;
<TR VALIGN=TOP>
	<TD $LIGHT><FONT $DARKTEXT SIZE=2>Area</TD>
	<TD BGCOLOR="$GREY"><FONT $DARKTEXT SIZE=1>$wx{Coverage}</TD>
</TR>
<TR VALIGN=TOP $MEDIUM>
	<TD><FONT SIZE=2>Credits:</TD>
	<TD BGCOLOR="$DARKGREY"><FONT SIZE=1>$ME - by <A HREF="mailto:msolomon\@seva.net">Mark Solomon</A><BR>
		Data retrieved from <A HREF="$wx{URL}">$wx{URL}</A> and processed by <A HREF="http://www.seva.net/~msolomon/wx/dist/">this perl script.</A></TD>
</TR>
</TD></TR></TABLE>
</TD></TR></TABLE>
</TD></TR></TABLE>

<FONT $LIGHTTEXT SIZE=2>
<FORM METHOD=POST>
	New City <INPUT NAME='city' SIZE=20 VALUE="$city">
	State <INPUT SIZE=3 MAXLENGTH=2 NAME='state' TYPE=text VALUE="$state">
	<INPUT TYPE=SUBMIT VALUE='Get Wx'>
</FORM>
Also note that I've made a much <A HREF="front/">snazzier version of this page</A>, if that's your taste.
<HR WIDTH="550" NOSHADE>
</FONT>
<FONT SIZE=2><I>&copy; 1998 Mark Solomon</I></FONT>
</CENTER>
ENDBOTTOM

print $out . "\n"; 
exit(0);
