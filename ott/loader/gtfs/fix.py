import os
import csv

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase


class Fix(CacheBase):
    """
    cmd line utility that opens a GTFS file, and can rename agency in routes/agency .txt files
    why this exists, I forget :-(  that said, I can think of a handful of times I had to manually fix a gtfs file, so...
    older comments below indicate this was created to match TriMet's gtfs-rt PSC alerts with the gtfs.zip data
    """
    gtfs_name = None
    gtfs_path = None

    def __init__(self, gtfs_name):
        super(Fix, self).__init__(section='gtfs')
        self.gtfs_name = gtfs_name
        self.gtfs_path = os.path.join(self.cache_dir, gtfs_name)

    def cp(self, to_gtfs_path=None):
        """ copy gtfs file to new file (good for testing, so you don't harm original gtfs.zip)
        """
        if to_gtfs_path is None:
            to_gtfs_path = self.gtfs_path + '.zip'
        file_utils.cp(self.gtfs_path, to_gtfs_path)
        self.gtfs_path = to_gtfs_path

    def rename_agency_in_routes_txt(self, regex_str, replace_str):
        file_utils.replace_strings_in_zipfile(self.gtfs_path, "routes.txt", regex_str, replace_str)

    def rename_agency_in_agency_txt(self, regex_str, replace_str):
        file_utils.replace_strings_in_zipfile(self.gtfs_path, "agency.txt", regex_str, replace_str)

    def find_stops(self, stop, file_name="stop_times.txt"):
        """ grep something from stop_times.txt """

        # step 1: create the stop search ... thing we'll be looking for
        ss = ",{},".format(stop)
        print("going to search for {}".format(ss))

        # step 2: extract file from gtfs -- open temp file to write stuff
        file_path = file_utils.unzip_file(self.gtfs_path, file_name)
        fp = open(file_path + ".tmp", "w+")

        # step 3: read/write (to tmp) loop
        first_line = None
        prev_line = None
        with open(file_path) as infile:
            for line in infile:
                if first_line is None:
                    first_line = line
                if ss in line and prev_line:
                    import pdb; pdb.set_trace()
                    # step 4: HACK - compare trip ids of 2 lines for match
                    ls = line.split(",")
                    ps = prev_line.split(",")
                    if ls[0] == ps[0]:
                        # step 5: break line
                        li = line.index(ss) + len(ss)
                        nl = "{}{}".format(line[0:li], prev_line[li:])
                        print(nl)

                        # step 5: rewrite newly fixed line
                        fp.write(line)
                        prev_line = None
                        continue

                # step N: write and save line
                if prev_line:
                    fp.write(prev_line)
                prev_line = line

        if prev_line:
            fp.write(prev_line)


    @classmethod
    def get_args(cls):
        """ command-line arg parser and help util...
            examples:
               bin/gtfs_fix SAM.zip -a -r -f "^86" -t "SAM"
               bin/gtfs_fix SMART.zip -a -r -f "^108" -t "SMART"
        """
        import argparse
        parser = argparse.ArgumentParser(prog='gtfs-fix', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('gtfs', help="Name of GTFS zip that is in the 'cache' (e.g., TRIMET.zip)")
        parser.add_argument('--regex',   '-f', help="string (regex) to find in files")
        parser.add_argument('--replace', '-t', help="string to replace found regex strings")
        parser.add_argument('--routes',  '-r', default=False, action='store_true', help='fix routes.txt')
        parser.add_argument('--agency',  '-a', default=False, action='store_true', help='fix agency.txt')
        parser.add_argument('--copy',    '-c', default=False, action='store_true', help="make a copy of the gtfs.zip (don't edit original")
        parser.add_argument('--stop',    '-s', default=False, help="test stop query")
        args = parser.parse_args()
        return args


def rename_trimet_agency():
    """ just rename routes.txt (good for OTP alerts) ... don't rename the agency.txt
        bin/gtfs_fix TRIMET.zip -r -f "(PSC|TRAM)" -t "TRIMET"
    """
    fix = Fix("TRIMET.zip")
    fix.rename_agency_in_routes_txt("(PSC|TRAM)",  "TRIMET")


def main():
    args = Fix.get_args()
    fix = Fix(args.gtfs)
    if args.copy:
        fix.cp()
    if args.routes:
        fix.rename_agency_in_routes_txt(args.regex, args.replace)
    if args.agency:
        fix.rename_agency_in_agency_txt(args.regex, args.replace)
    if args.stop:
        fix.find_stops(args.stop)


if __name__ == '__main__':
    main()
