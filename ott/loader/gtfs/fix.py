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
    def rename_sam_agency(cls):
        fix = Fix("SAM.zip")
        fix.rename_agency_in_routes_txt("^86", "SAM")
        fix.rename_agency_in_agency_txt("^86", "SAM")

    @classmethod
    def rename_trimet_agency(cls):
        ''' don't rename the agency.txt ... just rename routes (good for OTP) '''
        fix = Fix("TRIMET.zip")
        fix.rename_agency_in_routes_txt("PSC",  "TRIMET")
        fix.rename_agency_in_routes_txt("TRAM", "TRIMET")


def main():
    
    fix = Fix()
    fix.cp()
    fix.rename_agency_in_routes_txt("^101", "SMART")
    fix.rename_agency_in_agency_txt("^101", "SMART")

if __name__ == '__main__':
    main()
