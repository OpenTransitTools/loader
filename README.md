loader
======

The loader project contains multiple utilities to load GTFS, OSM and OTP data into various apps and databases. The
sub projects are:
  1. otp.loader.gtfs, which contains routines to cache and compare gtfs feeds.
  1. otp.loader.otp,


build:
  0. install python 2.7, along easy_install, zc.buildout ("zc.buildout==1.5.2") and git
  1. git clone https://github.com/OpenTransitTools/loader.git
  2. cd loader
  3. buildout
  4. git update-index --assume-unchanged .pydevproject

run:
  1. bin/otp_tests -- runs the OTP graph tests
  2. ...
