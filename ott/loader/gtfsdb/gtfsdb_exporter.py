from .gtfsdb_loader import GtfsdbLoader


class GtfsdbExporter(GtfsdbLoader):
    """
    has various menthods to do the following:
     - use pg_dump to export a gtfsdb database / schema
     - scp the dump files to other servers
     - use pg_load to load a dump file into a clean db
    """
    def __init__(self):
        pass
