#!/usr/bin/perl -T
#
#	Get local Wx data from http://iwin.nws.noaa.gov/iwin/va/zone.html,
#	find the local zone, and place this data in a file.
#
#	3/2/98 Mark Solomon <msolomon@seva.net>
#	Copyright 1998 Mark Solomon (See GNU GPL)
#	$Id: wx.cgi,v 3.16 1998/11/11 14:33:18 msolomon Exp $
#	$Name:  $
#	11/98 Added ability to feed a background color as an argument using
#		'?BGCOLOR=808000' on the URL, etc.
#

use lib '.';
use Geo::WeatherNOAA;
use CGI;

use LWP::UserAgent;

BEGIN {
	$ENV{PATH} = '/usr/bin:/bin';
	$ENV{CDPATH} = '';
}

# my $ua = new LWP::UserAgent;
# $ua->proxy(['http', 'ftp'], 'http://www.seva.net:8001/');


my $VERSION = do { my @r = (q$Revision: 3.16 $ =~ /\d+/g); sprintf "%d."."%02d" x $#r, @r };
my $ME = ( split('/',$0) )[-1] . " $VERSION";

my $q = new CGI;
my $self = $q->script_name;
my $width = 580;
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
	# I dont want to redirect to a waiting page for Virginia
}
elsif ( ! $q->param(REDIR) ) {
	$page_bg = $q->param(BGCOLOR) || '#e5e5e5';
	# my $MyURL = 'http://www.seva.net/~msolomon/wx/wx.cgi';
	my $mycity = $city;
	$mycity =~ tr/ /+/d;
	my $MyURL .= "${self}?city=$mycity&state=$state&REDIR=1";
	print "Content-type:text/html\n\n";
	print '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">';
	print "<HTML><HEAD><TITLE>Mark's Local Wx</TITLE>\n";
	print "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=$MyURL\">\n";
	print "</HEAD>\n";
	print "<BODY BGCOLOR=\"$page_bg\">\n";
	print "<H2>Please wait, collecting weather data from NOAA</H2>\n";
	print "Although this server caches weather for the state of Virginia automatically, other states' data needs to be retreived.\n";
	print "<HR WIDTH=\"75%\">\nIf your browser is not currently trying to load the weather data page, <A HREF=\"$MyURL\">try this link.</A>\n";
	print "<HR WIDTH=\"75%\">\n<CENTER><FONT SIZE=2><I>Copyright &copy; 1998 Mark Solomon</I></FONT></CENTER>\n";
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

$forecast 	= get_currentWX_html($city,$state,30);

$page_bg = $q->param(BGCOLOR) || '#e5e5e5';
$out = $q->header,"\n";
$out .= $q->start_html(-title=>"Mark's Local Wx for $city, $state",-bgcolor=>$page_bg);
$out .= "<CENTER>\n";
$out .= "<TABLE WIDTH=$width CELLPADDING=0 CELLSPACING=0 BORDER=0><TR><TD>\n";
$out .= "<FONT SIZE=1>According to <A HREF=\"http://www.noaa.gov\">NOAA</A>:</FONT>\n";
$out .= "</TD></TR></TABLE>\n";
$out .= "<TABLE WIDTH=$width CELLPADDING=0 CELLSPACING=0 BORDER=0 BGCOLOR=\"#000000\"><TR><TD>\n";
$out .= "<TABLE WIDTH=$width CELLPADDING=4 CELLSPACING=1 BORDER=0 BGCOLOR=\"#000000\">\n";
$out .= "<TR><TD $MEDIUM><FONT $MEDIUMTEXT SIZE=\"+2\">Current weather for $city, $state</FONT></TD>\n";
$out .= "<TR><TD BGCOLOR=\"$GREY\"><FONT $LIGHTTEXT>$forecast</FONT>";
$out .= "</TD></TR></TABLE>\n";
$out .= "</TD></TR></TABLE>\n<BR>\n";


######
#
# Script is fine until here.
# Let's start rewriting (7/22/98) MS
#
######

%wx 		= get_forecast($city,$state,30);

$wx{Date} =~ s/^(\d+)(\d\d)\s(AM|PM)\s(\w+)\s(\w+)\s(\w+)\s0*(\d+)/$1:$2\L$3\E ($4) \u\L$5\E\E \u\L$6 $7,/;

# Pre-process warnings and data items
###########################################
@WARNINGS = ();
@FORECAST = ();
my @NEAR = split "\n", $wx{NEAR};
foreach $item (@NEAR) {
	my ($day,$data) = split(':',$item);
	if ($data) {
		push @FORECAST, "$day:$data";
	}
	else {
		push @WARNINGS, $day;
	}
}

$out .= run_list('WARNINGS','FORECAST',"Forecast Updated $wx{Date}") if (@NEAR);

@WARNINGS = ();
@FORECAST = ();
@EXTENDED = split "\n", $wx{EXTENDED};
foreach $item (@EXTENDED) {
	my ($day,$data) = split(':',$item);
	if ($data) {
		push @FORECAST, "$day:$data";
	}
	else {
		push @WARNINGS, $day;
	}
}
$out .= run_list('WARNINGS','EXTENDED','Extended Forecast:') if (@EXTENDED);

sub run_list {
	my ($warn_list, $forecast_list,$title) = @_;
	return if ! $#$forecast_list eq 0;

	# De-reference
	my @WARNINGS = @$warn_list;
	my @FORECAST = @$forecast_list;

	# print "WARNINGS: @WARNINGS\n"; exit(11);

	# Declare
	my $retText = '';
	my ($toprow,$bottomrow);
	my $cols = $#FORECAST + 1;

	$retText = "<TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0 WIDTH=$width BGCOLOR=\"#000000\"><TR><TD>\n";
	$retText.= "<TABLE CELLPADDING=4 CELLSPACING=1 BORDER=0 WIDTH=$width BGCOLOR=\"#000000\">\n";
	if ($title) {
		$retText .= "<TR BGCOLOR=\"$DARKGREY\"><!-- Separator/title $warning_flag -->\n";
		$retText .= "\t<TD COLSPAN=$cols VALIGN=BOTTOM>\n";
		$retText .= "\t<FONT $LIGHTTEXT SIZE=\"+1\">$title</FONT></TD>\n</TR>\n";
	}
	foreach $item (@WARNINGS) {
		$retText .= "\n<!-- Warning -->";
	      	$retText .= "\n<TR>\n\t<TD BGCOLOR=\"$RED\" COLSPAN=\"$cols\" ALIGN=CENTER>";
		$retText .= "\n\t<FONT COLOR=\"$DARKRED\">$item</FONT></TD>\n</TR>\n";
	}

	my $gif;
	foreach $item (@FORECAST) {
		my ($day,$data) = split(':',$item);
		$day or $day = '&nbsp;';
		$data =~ tr/\r\n//d;
		$data =~ s/^\s$//;
		$gif = 'none.gif';
		if ($data =~ /thunderstorm/i) {
			$gif = 'light.gif';
		}
		elsif ($data =~/(rain|drizzle)/i) {
			$gif = 'rain.gif';
		}
		elsif ($data =~/(snow|flurri)/i) {
			$gif = 'snow.gif';
		}
		elsif ($data =~ /mostly cloudy/i) {
			$gif = 'mocloudy.gif';
		}
		elsif ($data =~ /partly cloudy/i) {
			$gif = 'ptcloudy.gif';
		}
		elsif ($data =~ /cloud/i) {
			$gif = 'cloudy.gif';
		}
		elsif ($data =~ /partly sunny/i) {
			$gif = 'ptcloudy.gif';
		}
		elsif ($data =~ /mostly sunny/i) {
			$gif = 'mosunny.gif';
		}
		elsif ($data =~ /freez/i) {
			$gif = 'freeze.gif';
		}
		elsif ($data =~ /(sunny|clear)/i) {
			$gif = 'sunny.gif';
		}
		$toprow .= "\n	<TD $LIGHT VALIGN=BOTTOM>\n";
		$toprow .= "		<TABLE WIDTH=\"100%\" BORDER=0 CELLPADDING=0 CELLSPACING=0>\n";
		$toprow .= "		<TR><TD><FONT $DARKTEXT><NOBR>$day</NOBR></FONT></TD>\n";
		$toprow .= "		<TD ALIGN=RIGHT><IMG SRC=\"$gif\" ALT=\"\" WIDTH=36 HEIGHT=20></TD>\n";
		$toprow .= "		</TR></TABLE>\n";
		$toprow .= "	</TD>";
        	$bottomrow .= "\n\t<TD BGCOLOR=\"$GREY\">\n";
		$bottomrow .= "		<FONT $LIGHTTEXT>$data</FONT>\n\t</TD>";

	}
	$retText .= "<TR> <!-- Top Row -->$toprow</TR>\n";
	$retText .= "<TR VALIGN=TOP> <!-- Bottom Row --> $bottomrow</TR>\n";
	$retText .= "</TABLE> <!-- Inside Table -->\n";
	$retText .= "</TD></TR></TABLE> <!-- Outside Table -->\n<BR>\n";
	return $retText;
} # run_list()


$wx{Coverage} ||= 'No data available for area requested';

$out .= "<TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0 WIDTH=$width BGCOLOR=\"#000000\"><TR><TD>\n";
$out .= "<TABLE CELLPADDING=4 CELLSPACING=1 BORDER=0 WIDTH=$width BGCOLOR=\"#000000\">\n";
$out .= <<ENDBOTTOM;
<TR VALIGN=TOP>
	<TD $LIGHT><FONT $DARKTEXT SIZE=2>Area</FONT></TD>
	<TD BGCOLOR="$GREY"><FONT $DARKTEXT SIZE=1>$wx{Coverage}</FONT></TD>
</TR>
<TR VALIGN=TOP $MEDIUM>
	<TD><FONT SIZE=2>Credits:</FONT></TD>
	<TD BGCOLOR="$DARKGREY"><FONT SIZE=1>$ME, Geo::WeatherNOAA $Geo::WeatherNOAA::VERSION - by <A HREF="mailto:msolomon\@seva.net">Mark Solomon</A><BR>
		Data retrieved from <A HREF="$wx{URL}">$wx{URL}</A> and processed by <A HREF="http://www.seva.net/~msolomon/wx/dist/">this perl script.</A></FONT></TD>
</TR>
</TABLE>
</TD></TR></TABLE>

<FONT $LIGHTTEXT SIZE=2>
<FORM METHOD=POST ACTION=\"$self\">
	New City <INPUT NAME=\"city\" SIZE=20 VALUE="$city">
	State <INPUT SIZE=3 MAXLENGTH=2 NAME=\"state\" TYPE=text VALUE="$state">
	<INPUT TYPE=SUBMIT VALUE=\"Get Wx\">
</FORM>
<A HREF="./wx.cgi?city=outer+banks&state=nc">Outer Banks, NC</A> | 
<A HREF="./wx.cgi?city=new+york&state=ny">New York,NY</A> | 
<A HREF="./wx.cgi?city=boston&state=ma">Boston, MA</A> |
<A HREF="./wx.cgi?city=dover&state=de">Dover, DE</A> |
<A HREF="./wx.cgi?city=chicago&state=il">Chicago, IL</A>
</FONT>
<!-- <HR WIDTH="$width" NOSHADE>  -->
<BR>
<FONT SIZE=2><I>&copy; 1998 Mark Solomon</I></FONT>
</CENTER>
</BODY>
</HTML>
ENDBOTTOM
# Also note that I've made a much <A HREF="front/">snazzier version of this page</A>, if that's your taste.

print $out . "\n"; 
exit(0);
