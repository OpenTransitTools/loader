import os
import logging
log = logging.getLogger(__file__)

from ott.utils import object_utils
from ott.utils.cache_base import CacheBase


class SobiCache(CacheBase):
    """ cache a SOBI .json file
        @see http://socialbicycles.com/
    """
    url = None
    name = None
    file_name = None
    file_path = None

    def __init__(self):
        super(SobiCache, self).__init__(section='sobi')
        self.url = self.config.get('download_url')
        self.name = self.config.get('name')
        self.file_name = self.name + ".json"
        self.file_path = os.path.join(self.cache_dir, self.file_name)

    def check_feed(self, force_update=False):
        return self.simple_cache_item_update(self.file_name, self.url, force_update)


def main():
    #import pdb; pdb.set_trace()
    sobi = SobiCache()
    sobi.check_feed(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
