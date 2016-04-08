import os
import inspect
import shutil
import logging
logging.basicConfig(level=logging.INFO)

from ott.utils import file_utils

class Base(object):
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    @classmethod
    def get_tmp_dir(cls):
        tmp_dir = os.path.join(cls.this_module_dir, "tmp")
        file_utils.mkdir(tmp_dir)
        return tmp_dir

    @classmethod
    def get_cached_file(cls, gtfs_zip_name, dir=None, def_name="cache"):
        cache_dir = cls.get_cache_dir(dir, def_name)
        file = os.path.join(cache_dir, gtfs_zip_name)
        return file

    @classmethod
    def get_cache_dir(cls, cache_dir=None):
        ''' returns dir path ... makes the directory if it doesn't exist
        '''
        if cache_dir is None:
            cache_dir = os.path.join(cls.this_module_dir, "cache")
        file_utils.mkdir(cache_dir)
        return cache_dir

    @classmethod
    def cp_cached_file(cls, file_name, destination_dir, dir=None, def_name="cache"):
        file = cls.get_cached_file(file_name, dir, def_name)
        dest = os.path.join(destination_dir, file_name)
        shutil.copyfile(file, dest)

    @classmethod
    def get_url_filename(cls, gtfs_struct):
        url  = gtfs_struct.get('url')
        name = gtfs_struct.get('name', None)
        if name is None:
            name = file_utils.get_file_name_from_url(url)
        return url, name
