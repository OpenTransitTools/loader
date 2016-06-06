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

    def cp(cls, to_gtfs_path, filter_file_names):
        pass

    def rename_agency(self, agency_name="TRIMET", cp_file_name=None):
        '''
        '''
        file_utils.cp(self.gtfs_path, self.gtfs_path + '.zip')
        self.gtfs_path = self.gtfs_path + '.zip'

        file_utils.unzip_file(self.gtfs_path, file_name="routes.txt")
        file_utils.remove_file_from_zip(self.gtfs_path, file_name="routes.txt")


def main():
    #import pdb; pdb.set_trace()
    # fix = Fix("TRIMET.zip")
    fix = Fix("SAM.zip")
    fix.rename_agency()

if __name__ == '__main__':
    main()
