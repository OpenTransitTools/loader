import os
import logging
import logging.config
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


from ott.utils import file_utils
from ott.utils import object_utils
from ott.utils.cache_base import CacheBase

from ott.loader.gtfs.info import Info
from ott.loader.gtfs.diff import Diff

class GtfsCache(CacheBase):
    """ Does a 'smart' cache of a gtfs file
         1. it will look to see if a gtfs.zip file is in the cache, and download it and put it in the cache if not
         2. once cached, it will check to see that the file in the cache is the most up to date data...
    """
    feeds = []

    def __init__(self):
        super(GtfsCache, self).__init__(section='gtfs')
        self.feeds = self.config.get_json('feeds')

    def check_cached_feeds(self, force_update=False):
        for f in self.feeds:
            url,name = GtfsCache.get_url_filename(f)
            self.check_feed(url, name, force_update)

    def check_feed(self, url, file_name, force_update=False):
        ''' download feed from url, and check it against the cache
            if newer, then replace cached feed .zip file with new version
        '''
        # step 1: file name
        file_name = file_name
        file_path = os.path.join(self.cache_dir, file_name)

        # step 2: download new gtfs file
        url = url
        tmp_path = os.path.join(self.tmp_dir, file_name)
        file_utils.wget(url, tmp_path)

        # step 3: check the cache whether we should update or not
        update = force_update
        if not force_update:
            if self.is_fresh_in_cache(file_path):
                log.info("diff {} against cached {}".format(tmp_path, file_path))
                diff = Diff(file_path, tmp_path)
                if diff.is_different():
                    update = True
            else:
                update = True

        # step 4: mv old file to backup then mv new file in tmp dir to cache
        if update:
            log.info("move {} to cache {}".format(tmp_path, file_path))
            file_utils.bkup(file_path)
            file_utils.mv(tmp_path, file_path)

    def cmp_file_to_cached(self, gtfs_zip_name, cmp_dir):
        ''' returns a Diff object with cache/gtfs_zip_name & cmp_dir/gtfs_zip_name
        '''
        cache_path = os.path.join(self.cache_dir, gtfs_zip_name)
        other_path = os.path.join(cmp_dir, gtfs_zip_name)
        diff = Diff(cache_path, other_path)
        return diff

    @classmethod
    def _get_info(cls, gtfs_zip_name, file_prefix=''):
        ''' :return an info object for this cached gtfs feed
        '''
        cache_path = os.path.join(cls.get_cache_dir(), gtfs_zip_name)
        ret_val = Info(cache_path, file_prefix)
        return ret_val

    @classmethod
    def check_gtfs_zip_against_cache(cls, gtfs_zip, app_dir):
        ''' check the ott.loader.gtfs cache for any feed updates
        '''
        ret_val = False
        try:
            cache = GtfsCache()
            url, name = GtfsCache.get_url_filename(gtfs_zip)
            diff = cache.cmp_file_to_cached(name, app_dir)
            if diff.is_different():
                cache.cp_cached_file(name, app_dir)
                ret_val = True
        except Exception, e:
            log.warn(e)
        return ret_val

    @classmethod
    def check_gtfs_files_against_cache(cls, gtfs_zip_files, app_dir):
        ''' check the ott.loader.gtfs cache for any feed updates
        '''
        ret_val = False
        for g in gtfs_zip_files:
            c = GtfsCache.check_gtfs_zip_against_cache(g, app_dir)
            if c:
                ret_val = True
        return ret_val

    @classmethod
    def get_url_filename(cls, gtfs_struct):
        url  = gtfs_struct.get('url')
        name = gtfs_struct.get('name', None)
        if name is None:
            name = file_utils.get_file_name_from_url(url)
        return url, name


def main():
    #import pdb; pdb.set_trace()
    cache = GtfsCache()
    cache.check_cached_feeds(force_update=object_utils.is_force_update())

if __name__ == '__main__':
    main()
