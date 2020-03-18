import os
import csv

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase

import logging
log = logging.getLogger(__file__)


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

    def remove_deadhead_stop_times(self, stop, cull, perms=False, file_name="stop_times.txt", repack=True):
        """
        will remove preceding stop_time in a trip given a target stop

        THIS:
          9683134,18:01:00,18:01:00,9654,1,Portland,1,0,0.0,1,,
          9683134,18:03:00,18:03:00,8169,2,Portland,0,1,267.5,1,,

        BECOMES:
          9683134,18:03:00,18:03:00,8169,1,Portland,0,0,0.0,1,,

        grep a stop from stop_times.txt (w/in a gtfs.zip feed file)
        writes a stop_times.txt.tmp file with
        got dict read/write ideas from:
          https://stackoverflow.com/questions/2982023/how-to-write-header-row-with-csv-dictwriter/2982117
        """

        # step 0: warn if things don't look right
        if cull is False and perms is False:
            log.warning(" NOTE: since gtfs_fix is not going to do anything to the file {} in \n feed {}".format(file_name, self.gtfs_path))
            log.warning(" --cull (remove preceding stop in stop_times.txt) and/or --perms (change board & alight) need to be specified")
            return
        if file_utils.exists(self.gtfs_path) is False:
            log.error("gtfs file {} does not exist".format(self.gtfs_path))
            return

        # step 1: extract file from gtfs -- open temp file to write stuff
        in_file = file_utils.unzip_file(self.gtfs_path, file_name)
        out_file = in_file + ".tmp"

        # step 2: open this input csv
        with open(in_file, 'r') as csv_in:
            dr = csv.DictReader(csv_in)
            prev_row = None
            perm_count = 0
            cull_count = 0

            # step 3: open .csv output
            with open(out_file, 'w+') as csv_out:
                dw = csv.DictWriter(csv_out, fieldnames=dr.fieldnames)
                dw.writerow(dict(zip(dr.fieldnames, dr.fieldnames)))
                for row in dr:
                    # step 4: find target stop and process...
                    if row.get('stop_id') == stop:
                        # step 4a: set perms to board & alight
                        if perms:
                            row['pickup_type'] = "0"
                            row['drop_off_type'] = "0"
                            perm_count += 1

                        # step 4n: NOTE: any other stop_time work must preceed step 4z due to the 'continue' below

                        # step 4z: cull the preceding stop_time to our target stop, and move a few vars over
                        if cull and prev_row and row.get('trip_id') == prev_row.get('trip_id'):
                            row['stop_sequence'] = prev_row['stop_sequence']
                            row['shape_dist_traveled'] = prev_row['shape_dist_traveled']
                            dw.writerow(row)
                            prev_row = None
                            cull_count += 1
                            continue

                    # step 5: write out normal (prev) row and move on to next row
                    if prev_row:
                        dw.writerow(prev_row)
                    prev_row = row

                # step 6: outside the read/write loop, write last row
                if prev_row:
                    dw.writerow(prev_row)

            log.warning("culls {}\nperms changes {}".format(cull_count, perm_count))

        if repack:
            log.warning("repacking {} into {}".format(file_name, self.gtfs_path))
            file_utils.replace_file_in_zipfile(self.gtfs_path, out_file, file_name)
        else:
            log.warning("changes saved to file {}".format(out_file))


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
        parser.add_argument('--replace', '-t', help="string to replace found regex strings")
        parser.add_argument('--regex',   '-f', help="string (regex) to find in files")
        parser.add_argument('--routes',  '-r', default=False, action='store_true', help='fix routes.txt')
        parser.add_argument('--agency',  '-a', default=False, action='store_true', help='fix agency.txt')
        parser.add_argument('--copy',   '-cp', default=False, action='store_true', help="make a copy of the gtfs.zip (don't edit original")

        parser.add_argument('--stop',    '-s', default=False, help="change gtfs.zip/stop_times.txt to eliminate previous stop from trip (e.g., BTC deadhead / boarding 8169)")
        parser.add_argument('--perms',   '-p', default=False, action='store_true', help="change stop board/alight permissions")
        parser.add_argument('--cull',    '-c', default=False, action='store_true', help="cull previous stop_time (deadhead)")

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
        fix.remove_deadhead_stop_times(args.stop, args.cull, args.perms)


if __name__ == '__main__':
    main()
