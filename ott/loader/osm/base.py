import os
import inspect
import shutil
import logging
logging.basicConfig(level=logging.INFO)

from ott.loader.gtfs import utils

class Base(object):
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    @classmethod
    def get_tmp_dir(cls):
        tmp_dir = os.path.join(cls.this_module_dir, "tmp")
        utils.mkdir(tmp_dir)
        return tmp_dir

    @classmethod
    def get_cache_dir(cls, dir=None, def_name="cache"):
        ''' returns either dir (stupid check) or <current-directory>/$def_name
        '''
        ret_val = dir
        if dir is None:
            ret_val = os.path.join(cls.this_module_dir, def_name)
        utils.mkdir(ret_val)
        return ret_val

    @classmethod
    def get_cached_file(cls, gtfs_zip_name, dir=None, def_name="cache"):
        cache_dir = cls.get_cache_dir(dir, def_name)
        file = os.path.join(cache_dir, gtfs_zip_name)
        return file

    @classmethod
    def cp_cached_gtfs_zip(cls, gtfs_zip_name, destination_dir, dir=None, def_name="cache"):
        file = cls.get_cached_file(gtfs_zip_name, dir, def_name)
        dest = os.path.join(destination_dir, gtfs_zip_name)
        shutil.copyfile(file, dest)

    @classmethod
    def get_url_filename(cls, gtfs_struct):
        url  = gtfs_struct.get('url')
        name = gtfs_struct.get('name', None)
        if name is None:
            name = utils.get_file_name_from_url(url)
        return url, name
