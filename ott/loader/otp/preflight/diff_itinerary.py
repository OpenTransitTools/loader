import sys
import time
import logging
import traceback
import re
import filecmp
import urllib2
import socket


class DiffItinerary(object):
    """ call a given url X number of times, strip out the variable pieces (currently the <date>timestamp here</date> stuff
        and compare the output to each other...report back 
    """
    def __init__(self, url, name, date=None):
        self.url = url
        self.name = name
        self.date = date
        self.response_time = 0

    def call_otp(self, url, fname):
        """ calls the trip web service and saves the trip to a file fname
        """
        try:
            # step 1: get itinerary from OTP
            start = time.time()
            url = (url if url != None else self.get_planner_url())
            socket.setdefaulttimeout(20)
            req = urllib2.Request(url, None, {'Accept':'application/xml'})
            res = urllib2.urlopen(req)
            itinerary = res.read()
            res.close()
            end = time.time()
            self.response_time = end - start
            logging.info("call_otp: response time of {} second for url {}".format(self.response_time, url))

            # step 2: remove things like a file timestamp, and add newlines to each element (so we can compare)
            itinerary = self.remove_variable_stuff(itinerary)
            itinerary = self.add_newlines(itinerary)

            # step 3: save to a file
            logging.info("call_otp: writing itin to file {}".format(fname))
            f = open(fname, 'w')
            f.write(itinerary)
            f.flush()
            f.close()
        except:
            print('ERROR: could not get data from url:\n', url, '\n(not a friendly place)')
            traceback.print_exc(file=sys.stdout)
            pass

    def remove_variable_stuff(self, xml):
        """ remove things that are variable and change between web calls (like a timestamp, etc...)
        """
        xml = re.sub(r'<date.*date>', '', xml)
        return xml

    def add_newlines(self, xml):
        """ remove things that are variable and change between web calls (like a timestamp, etc...)
        """
        xml = re.sub(r'>', '>\n', xml)
        return xml

    def make_outfile_name(self, index):
        return "{0}-{1}.{2}".format(self.name, index, "txt")

    def compare(self, count=40, sleep=1):
        """ 
        """
        errors = False
        result = []
        for i in range(1,count):
            f1 = self.make_outfile_name(i)
            f2 = self.make_outfile_name(i+1)
            if filecmp.cmp(f1, f2) is False:
                errors = True
                result.append({'file1':f1, 'file2':f2})
        return errors,result

    def run(self, count=40, sleep=2):
        """ 
        """
        for i in range(1,count+1):
            self.call_otp(self.url, self.make_outfile_name(i))
            if sleep > 0:
                logging.info("diff_itinerary.run() sleeping for " + str(sleep) + " seconds")
                time.sleep(sleep)


def main():
    logging.basicConfig(level=logging.INFO)
    di = DiffItinerary("http://maps10.trimet.org/test?time=12:00pm&toPlace=45.552360%2C-122.852970&fromPlace=45.589850%2C-122.599266", "/tmp/otp-test")
    di = DiffItinerary("http://rtp.trimet.org/prod?time=12:00pm&fromPlace=4012%20SE%2017TH%20AVE::45.492620,-122.647500&toPlace=Zoo::45.509750,-122.714645&mode=BICYCLE&submit", "/tmp/otp-bike-test") 
    runs=3
    di.run(runs)
    res, lst = di.compare(runs)
    for i in lst:
        print(i['file1'],"is not equal to",i['file2'])


if __name__ == '__main__':
    main()
