import os

from ott.utils import file_utils
from ott.utils.cache_base import CacheBase


class Files(CacheBase):
    """
    class / cmd line utility that opens a GTFS file, and returns a file(s) from the feed.
    """
    gtfs_name = None
    gtfs_path = None

    def __init__(self, gtfs_name):
        super(Files, self).__init__(section='gtfs')
        self.gtfs_name = gtfs_name
        self.gtfs_path = os.path.join(self.cache_dir, gtfs_name)

    def stats(self):
        age = file_utils.file_age(self.gtfs_path)
        size = file_utils.file_size(self.gtfs_path)
        print("age: {}\nsize: {}".format(age, size))

    def export(self, file_name):
        """
        find a file in a .zip, unzip it, then return the path to that file
        """
        path = file_utils.unzip_file(self.gtfs_path, file_name)
        return path

    @classmethod
    def get_args(cls):
        """ command-line arg parser and help util...
            examples:
               bin/gtfs_fix SAM.zip -a -r -f "^86" -t "SAM"
               bin/gtfs_fix SMART.zip -a -r -f "^108" -t "SMART"
        """
        import argparse
        parser = argparse.ArgumentParser(prog='gtfs-file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('gtfs', help="Name of GTFS zip that is in the 'cache' (e.g., TRIMET.zip)")
        parser.add_argument('--find',  '-f', help='file(s) to find: agency.txt,feed_info.txt')
        args = parser.parse_args()
        return args


def main():
    # import pdb; pdb.set_trace()
    args = Files.get_args()
    f = Files(args.gtfs)
    f.stats()
    if args.find:
        flist = args.find.split(",")
        for i in flist:
            print(f.export(i))


if __name__ == '__main__':
    main()
