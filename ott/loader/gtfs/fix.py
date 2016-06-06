import os
import logging

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase


class Fix(CacheBase):
    """ Diff Two Gtfs Zip Files, looking at feed_info.txt & calendar_date.txt file to see differences between them
    """
    gtfs_name = None
    gtfs_path = None

    def __init__(self, gtfs_name):
        self.gtfs_name = gtfs_name
        self.gtfs_path = os.path.join(self.cache_dir, gtfs_name)

    def cp(self, to_gtfs_path=None):
        ''' copy gtfs file to new file (good for testing, so you don't harm original gtfs.zip)
        '''
        if to_gtfs_path is None:
            to_gtfs_path = self.gtfs_path + '.zip'
        file_utils.cp(self.gtfs_path, to_gtfs_path)
        self.gtfs_path = to_gtfs_path

    def rename_agency_in_routes_txt(self, regex_str, replace_str):
        file_utils.replace_strings_in_zipfile(self.gtfs_path, "routes.txt", regex_str, replace_str)

    def rename_agency_in_agency_txt(self, regex_str, replace_str):
        file_utils.replace_strings_in_zipfile(self.gtfs_path, "agency.txt", regex_str, replace_str)

    @classmethod
    def get_args(cls):
        ''' database load command-line arg parser and help util...

            examples:
               bin/gtfs_fix SAM.zip -a -r -f "^86" -t "SAM"
               bin/gtfs_fix SMART.zip -a -r -f "^108" -t "SMART"
        '''
        import argparse
        parser = argparse.ArgumentParser(prog='gtfs-fix', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('gtfs', help="Name of GTFS zip that is in the 'cache' (e.g., TRIMET.zip)")
        parser.add_argument('--regex',   '-f', required=True, help="string (regex) to find in files")
        parser.add_argument('--replace', '-t', required=True, help="string to replace found regex strings")
        parser.add_argument('--routes',  '-r', default=True,  action='store_true', help='fix routes.txt')
        parser.add_argument('--agency',  '-a', default=False, action='store_true', help='fix agency.txt')
        parser.add_argument('--copy',    '-c', default=False, action='store_true', help="make a copy of the gtfs.zip (don't edit original")
        args = parser.parse_args()
        return args


def rename_trimet_agency():
    ''' just rename routes.txt (good for OTP alerts) ... don't rename the agency.txt
        bin/gtfs_fix TRIMET.zip -r -f "(PSC|TRAM)" -t "TRIMET"
    '''
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

if __name__ == '__main__':
    main()
