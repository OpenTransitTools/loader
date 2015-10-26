

class Preflight(object):
    """ check the gtfsdb for proper tables and sizes
    """
    def __init__(self, config=None, gtfs_zip_files=Cache.get_gtfs_feeds()):
        self.gtfs_zip_files = gtfs_zip_files
