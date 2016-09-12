import os
import logging
import urllib2
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import web_utils
from ott.loader.solr.solr_cache import SolrCache


class SolrLoader(object):
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
    def load(cls):
        ''' run the SOLR loader, which post all cahce/*_add.xml files into SOLR
            NOTE: this is effectively a main method for sending solr/cache/*_add.xml files to SOLR
        '''
        loader = SolrLoader()
        loader.process_del_files()
        loader.process_add_files()

    def process_add_files(self):
        ''' find all cache/*_add.xml files and send them to SOLR
        '''
        files = file_utils.ls(self.cache.cache_dir, "_add.xml")
        for f in files:
            self._process_file(f, do_optimize=True)

    def process_del_files(self):
        ''' run thru all the <name_del.xml> files in the cache
            TODO: should I first check that an add file exists, and that it contains valid content?
        '''
        files = file_utils.ls(self.cache.cache_dir, "_del.xml")
        for f in files:
            self._process_file(f, do_optimize=False)

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
    def update_index(cls, url, solr_xml_file_path, do_optimize=False):
        ''' update a SOLR index via a single instance
            NOTE: if multiple instances of SOLR point to the same instance, only instance needs to call this routine
        '''
        status = cls.post_file(url, solr_xml_file_path)
        cls.commit(url)
        if do_optimize:
            cls.optimize(url)
        return status == 200

    def _process_file(self, file_name, do_optimize):
        ''' does the meat of the work in posting files to SOLR.
            the paths to SOLR instances are pulled from config/app.ini
            this routine will post to either a single SOLR instance, or manage multiple SOLR instances running
            on different ports.
        '''
        is_success = False

        # step 1: grab file path
        solr_xml_file_path = os.path.join(self.cache.cache_dir, file_name)
        log.debug(solr_xml_file_path)

        # step 2: grab SOLR properties for url (and optionally the web ports where SOLR instance(es) run
        url  = self.config.get('url')
        reload_url = self.config.get('reload')
        ports = None
        if ":{}" in url or ":{0}" in url:
            ports = self.config.get_list('ports', def_val='80')

        # step 3: update SOLR
        if ports:
            # step 3a: post the .xml content to the first SOLR instance
            u = url.format(ports[0])
            is_success = self.update_index(u, solr_xml_file_path, do_optimize)

            # step 3b: now refresh all instances of SOLR
            for p in ports:
                u = url.format(p)
                ru = reload_url.format(p) if reload_url else None

                # have to call commit a couple of times to make SOLR instances refresh
                self.commit(u)
                urllib2.urlopen(ru)
                self.commit(u)
                urllib2.urlopen(ru)
        else:
            # step 3c: update and refresh the single instance of SOLR
            is_success = self.update_index(url, solr_xml_file_path, do_optimize)

        # step 4: either warn us, or mv file to processed folder so it's not processed again...
        if not is_success:
            log.warn("something happened loading {} into SOLR".format(solr_xml_file_path))
        else:
            to_path = os.path.join(self.post_process_dir, file_name)
            file_utils.mv(solr_xml_file_path, to_path)

        return is_success

