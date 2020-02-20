loader
======

The loader project contains multiple utilities to load GTFS, OSM and OTP data into various apps and databases. The
sub projects are:
  1. [geocoder](ott/loader/geocoder/README.md), which creates data output for the Pelias geocoder
  1. [gtfs](ott/loader/gtfs/README.md), which contains routines to cache and compare gtfs feeds.
  1. [gtfsdb](ott/loader/gtfsdb/README.md), which loads gtfs files into GTFSDB
  1. [osm](ott/loader/osm/README.md), which downloads OSM .pdb files, and futher can extract .osm data via OSMOSIS
  1. [otp](ott/loader/otp/README.md), which builds graphs (Graph.obj) databases for [OpenTripPlanner](http://opentripplanner.org)
  1. [solr](ott/loader/solr/README.md), which has config and scripts for loading SOLR (a depricated geo search tool)
  1. [sum](ott/loader/sum/README.md), shared use mobility ... place to pull in car (Zipcar), bike (BIKETOWN) & e-scooter (LIME, BIRD, SHARED, etc...) data, etc...

install:
  1. install python 3.7 (works with py versions >= 2.7), zc.buildout and git
  1. git clone https://github.com/OpenTransitTools/loader.git
  1. cd loader
  1. buildout
  1. (note: if buildout fails, keep running ... possibly run scripts/clean*sh between runs of buildout ... you'll eventually get there)
  1. git update-index --assume-unchanged .pydevproject
  1. NOTE: system packages necessary for things to work may include pre-built Shapely, or else the following system packages: 
  1. Install these packages
     - `yum install protobuf protobuf-devel tokyocabinet tokyocabinet-devel geos geos-devel  libxml2 libxslt libxml2-devel libxslt-devel openssl-devel
    `
  1. Or Build and install Protobuf and TokyoCabinet from source (MacOSX):
     - git clone https://github.com/google/protobuf 
     - wget http://tokyocabinet.sourceforge.net/tokyocabinet-1.4.25.tar.gz
     


run:
  1. bin/test ... this cmd will run loader's unit tests (see: http://docs.zope.org/zope.testrunner/#some-useful-command-line-options-to-get-you-started)
  1. see individual project README's above to see different app runs
  1. and check out the bin/ generated after buildout is run (those binaries are created via buildout & setup.py)
