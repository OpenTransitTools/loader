deploy
======

scripts used to test OTP Graph.obj and deploy new OTP Graphs into production.
scripts used to update OSM data in a PostGIS db, etc...
scripts used to populate PostGIS for the OTT system

build:
  0. install python 2.7, along easy_install, zc.buildout ("zc.buildout==1.5.2") and git
  1. git clone https://github.com/OpenTransitTools/deploy.git
  2. cd deploy
  3. buildout
  4. git update-index --assume-unchanged .pydevproject

run:
  1. bin/otp_tests -- runs the OTP graph tests
  2. ...
