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
        """
        will remove preceding stop in trip given a target stop

        grep a stop from stop_times.txt (w/in a gtfs.zip feed file)
        writes a stop_times.txt.tmp file with
        got dict read/write ideas from:
          https://stackoverflow.com/questions/2982023/how-to-write-header-row-with-csv-dictwriter/2982117
        """

        # step 1: extract file from gtfs -- open temp file to write stuff
        in_file = file_utils.unzip_file(self.gtfs_path, file_name)

        # step 2: open this input csv
        with open(in_file, 'r') as csv_in:
            dr = csv.DictReader(csv_in)
            prev_row = None

            # step 3: open .csv output
            with open(in_file + ".tmp", 'w+') as csv_out:
                dw = csv.DictWriter(csv_out, fieldnames=dr.fieldnames)
                dw.writerow(dict(zip(dr.fieldnames, dr.fieldnames)))
                for row in dr:
                    # step 4: cull the preceding stop_time to our target stop, and move a few vars over
                    if prev_row and row.get('stop_id') == stop and row.get('trip_id') == prev_row.get('trip_id'):
                        row['stop_sequence'] = prev_row['stop_sequence']
                        row['shape_dist_traveled'] = prev_row['shape_dist_traveled']
                        row['pickup_type'] = "0"
                        row['drop_off_type'] = "0"
                        dw.writerow(row)
                        prev_row = None
                        continue

                    # step 5: write out normal (prev) row and move on to next row
                    if prev_row:
                        dw.writerow(prev_row)
                    prev_row = row

                # step 6: outside the read/write loop, write last row
                if prev_row:
                    dw.writerow(prev_row)

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
