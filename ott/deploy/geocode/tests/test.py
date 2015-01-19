import unittest

import urllib
import contextlib
import json

from ott.utils.parse import csv_reader

HOST="localhost:4444"
#HOST="maps7.trimet.org/ride_ws"

class TestGeoCoder(unittest.TestCase):
    def setUp(self):
        here = csv_reader.Csv.get_dirname(__file__)
        self.csv_file = csv_reader.Csv('geocodes.csv', here)
        self.test_data = self.csv_file.open()

    def tearDown(self):
        self.csv_file.close()
        pass

    def test_zoo(self):
        url = get_url('geocode', 'place=zoo')
        j = call_url(url)
        s = json.dumps(j)
        self.assertRegexpMatches(s,"-122.71")
        self.assertRegexpMatches(s,"45.51")


    def test_geocode_csv_data(self):
        for d in self.test_data:
            u = get_url('geostr', 'place=' + d['name'])
            s = call_url_text(u)
            self.assertRegexpMatches(s,d['lat'].strip())
            self.assertRegexpMatches(s,d['lon'].strip())


def get_url(svc_name, params=None):
    ret_val = "http://{0}/{1}".format(HOST, svc_name)
    if params:
        ret_val = "{0}?{1}".format(ret_val, params)
    return ret_val

def call_url(url):
    with contextlib.closing(urllib.urlopen(url)) as f:
        ret_json = json.load(f)
    return ret_json

def call_url_text(url):
    print url
    return urllib.urlopen(url).read()
