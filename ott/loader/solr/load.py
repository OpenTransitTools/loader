import os
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import web_utils
from ott.loader.solr.solr_cache import SolrCache


class Load(object):
    """ load GTFS data into a gtfsdb
    """
    cache = None
    config = None
    post_process_dir = None

    def __init__(self):
        self.cache = SolrCache()
        self.config = self.cache.config
        self.post_process_dir = os.path.join(self.cache.cache_dir, 'processed')
        file_utils.mkdir(self.post_process_dir)

    @classmethod
    def solr_loader(cls):
        '''
        '''
        loader = Load()
        loader.process_del_files()
        loader.process_add_files()

    def process_add_files(self):
        '''
        '''
        files = file_utils.ls(self.cache.cache_dir, "_add.xml")
        for f in files:
            self._process_file(f)

    def process_del_files(self):
        ''' run thru all the <name_del.xml> files in the cache
            TODO: should I first check that an add file exists, and that it contains valid content?
        '''
        files = file_utils.ls(self.cache.cache_dir, "_del.xml")
        for f in files:
            self._process_file(f)

    @classmethod
    def commit(cls, url):
        ''' send commit (<commit/>) message to SOLR, which persists index changes to SOLR
        '''
        status = web_utils.post_data(url, "<commit/>")
        if status != 200:
            log.info("HTTP STATUS: {} when posting a 'commit' command to SOLR instance {}".format(status, url))
        return status

    @classmethod
    def optimize(cls, url):
        ''' send optimize (<optimize/>) message to SOLR, which fixes up the SOLR instance
        '''
        status = web_utils.post_data(url, "<optimize/>")
        if status != 200:
            log.info("HTTP STATUS: {} when posting a 'optimize' command to SOLR instance {}".format(status, url))
        return status

    @classmethod
    def post_file(cls, url, solr_xml_file_path):
        ''' post a file to a SOLR instance
        '''
        status = web_utils.post_file(url, solr_xml_file_path)
        if status != 200:
            log.info("HTTP STATUS: {} when posting file {} command to SOLR instance {}".format(status, solr_xml_file_path, url))
        return status

    @classmethod
    def update_index(cls, url, solr_xml_file_path):
        ''' update a SOLR index via a single instance
            NOTE: if multiple instances of SOLR point to the same instance, only instance needs to call this routine
        '''
        status = cls.post_file(url, solr_xml_file_path)
        cls.commit(url)
        cls.optimize(url)
        return status == 200

    def _process_file(self, file_name):
        '''
        '''
        is_success = False

        # step 1: grab file path
        solr_xml_file_path = os.path.join(self.cache.cache_dir, file_name)
        log.debug(solr_xml_file_path)

        # step 2: grab SOLR properties for url (and optionally the web ports where SOLR instance(es) run
        url  = self.config.get('url')
        ports = None
        if ":{}" in url or ":{0}" in url:
            ports = self.config.get_list('ports', def_val='80')

        # step 3: update SOLR
        if ports:
            # step 3a: update one instance of SOLR (assumes they use a shared index)
            u = url.format(ports[0])
            is_success = self.update_index(u, solr_xml_file_path)

            # step 3b: refresh all instances of SOLR
            for p in ports[:-1]:
                u = url.format(p)
                self.commit(u)
        else:
            # step 3c: update and refresh the single instance of SOLR
            is_success = self.update_index(url, solr_xml_file_path)

        # step 4: mv file to processed folder
        if is_success:
            to_path = os.path.join(self.post_process_dir, file_name)
            file_utils.mv(solr_xml_file_path, to_path)

        return is_success
