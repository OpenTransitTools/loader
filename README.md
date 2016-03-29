loader
======

The loader project contains multiple utilities to load GTFS, OSM and OTP data into various apps and databases. The
sub projects are:
  1. otp.loader.gtfs, which contains routines to cache and compare gtfs feeds.
  1. otp.loader.otp,

build:
  1. install python 2.7, along easy_install, zc.buildout ("zc.buildout==1.5.2") and git
  1. git clone https://github.com/OpenTransitTools/loader.git
  1. cd loader
  1. buildout
  1. git update-index --assume-unchanged .pydevproject

run:
  1. bin/test ## runs loader tests for geocoder, etc... (see: http://docs.zope.org/zope.testrunner/#some-useful-command-line-options-to-get-you-started)
  1. bin/python ott/loader/gtfs/cache.py <url> ## cache gtfs feeds into ott/loader/gtfs/cache
  1. bin/python ott/loader/gtfs/cache.py ## cache trimet.org's gtfs feed
