loader:geocoder
===============

has cmd-line tools to generate data for Pelias
also has older data/maf_fixes.csv (Portland Metro master address fix), which fixes bad coordinates from the Metro .shp file 

ls bin/geocoder_export_* to see the different exporters 


------------------------
###### As of 2-20-20, BELOW IS OLD (possibly out of date) INFO:
...............................................................................

Load postgres geocoder (or other TBD geocoder).  
Test geocoder with a set of known addresses (current [test suite](./tests/geocodes.csv) is for Portland area).

Also is a repo for 'fixes' to addresses in the Portland Metro master address file, via [maf_fixes.csv](./data/maf_fixes.csv)

run: bin/test will run the address tests...
