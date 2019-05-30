from ott.utils import file_utils
from ott.utils import web_utils
from ott.utils import exe_utils
from ott.utils import db_utils

from .gtfsdb_loader import GtfsdbLoader

import logging
log = logging.getLogger(__file__)

# TODO:  make this class 'generic', and then override it with config junk, so it can be repurposed
# todo:  use this both here and for osm2pgsql ???

class GtfsdbExporter(GtfsdbLoader):
    """
    has various menthods to do the following:
     - use pg_dump to export a gtfsdb database / schema
     - scp the dump files to other servers
     - use pg_load to load a dump file into a clean db
    """
    def __init__(self):
        super(GtfsdbExporter, self).__init__()

    def dump_feed(self, feed):
        """ run the db dumper
        """
        ret_val = True
        feed_name = ""
        try:
            feed_name = self.get_feed_name(feed)
            dump_path = self.get_dump_path(feed_name)
            dump_exe = self.config.get('dump', section='db').format(schema=feed_name, dump_file=dump_path)
            log.info(dump_exe)
            exe_utils.run_cmd(dump_exe, shell=True)
        except Exception as e:
            ret_val = False
            log.error("DB DUMP ERROR {} : {}".format(feed_name, e))
        return ret_val

    def _scp_dump_file(self, feed, server, user):
        """
        scp gtfsdb dump file to a a given server.
        :returns path to the dump file
        """
        ret_val = None

        # step 1: create file paths to dump files locally, and also path where we'll scp these files
        feed_name = self.get_feed_name(feed)
        dump_path = self.get_dump_path(feed_name)
        gtfsdb_dir = self.config.get('gtfsdb_dir', section='deploy')

        # step 2: we are going to attempt to scp the dump file over to the server
        #         note: the server paths (e.g., graph_svr, etc...) are relative to the user's home account
        if file_utils.exists(dump_path):
            if file_utils.is_min_sized(dump_path, 200000):
                ret_val = dump_path

                scp = None
                try:
                    scp, ssh = web_utils.scp_client(host=server, user=user)

                    mkdir = "mkdir -p ~/{}".format(gtfsdb_dir)
                    log.info("ssh {} on {}@{}".format(mkdir, user, server))
                    ssh.exec_command(mkdir)

                    log.info("scp {} over to {}@{}:~/{}/".format(dump_path, user, server, gtfsdb_dir))
                    scp.put(dump_path, gtfsdb_dir)
                except Exception as e:
                    log.warn("{} -- feed={}, server={}, user={}".format(e, feed_name, server, user))
                    ret_val = False
                finally:
                    if scp:
                        scp.close()
            else:
                log.warn("{} is suspiciously SMaLl, so *not* going SCP it to {}".format(dump_path, server))
        else:
            log.warn("{} doesn't exit, so *not* going to SCP it to {}".format(dump_path, server))
        return ret_val

    def check_feeds(self, feeds):
        # make sure we have a list of 'feeds' objects (see app.ini for the structure of a feed object)
        if feeds is None:
            feeds = self.feeds
        elif not isinstance(feeds, (list, tuple)):
            feeds = [feeds]
        return feeds

    @classmethod
    def scp(cls, feeds=None, filter=None, rm_after_scp=True):
        """
        loop thru servers in app.ini [deploy], looking to scp the pg_dump file over to production
        :returns number of feeds that were scp'd
        """
        ret_val = 0
        exporter = GtfsdbExporter()
        user = exporter.config.get('user', section='deploy')
        for feed in exporter.check_feeds(feeds):
            dump_path = None
            num_scp = 0

            # scp the feed to the configured servers
            prod_servers = exporter.config.get_json('servers', section='deploy')
            for server in prod_servers:
                if filter is None or filter == 'all' or filter in server:
                    dump_path = exporter._scp_dump_file(feed, server, user)
                    if dump_path:
                        num_scp += 1

            # move the dump.tar aside (but don't delete it), so it doesn't repeatedly get scp'd
            if dump_path and rm_after_scp:
                file_utils.mv(dump_path, dump_path + "-did_scp")

            # report on number of times we scp'd to different servers, etc...
            if num_scp > 0:
                ret_val += 1  # number of feeds scp'd
                num_servers = len(prod_servers)
                feed_name = exporter.get_feed_name(feed)
                if num_scp != num_servers:
                    log.warn("Tried to scp feed {} to {} production servers, but only able to scp {} times.".format(
                        feed_name,
                        num_servers,
                        num_dumped
                    ))
                else:
                    log.info("successfully scp'd feed {} to {} production servers".format(feed_name, num_servers))
        return ret_val

    @classmethod
    def dump(cls, feeds=None, filter=None, clean_db=False):
        """
        call pg_dump on a given feed or list of feeds
        can 'filter' the names of feeds also
        :returns count of feeds dumped
        """
        ret_val = 0

        # step 1: create the db and check the feeds that they're a list/tuple of feeds...
        # import pdb; pdb.set_trace()
        db = GtfsdbExporter()
        feeds = db.check_feeds(feeds)

        # step 2: process the feeds
        if feeds and len(feeds) > 0:
            # step 3: clean the database before exporting
            if clean_db:
                db_utils.postgres_db_cleanup()

            # step 4: dump them feeds
            for f in feeds:
                if filter and filter.lower() != 'all' and filter.lower() not in f.get('name').lower():
                    continue
                db.dump_feed(f)  # agency not filtered, so dump it
                ret_val += 1

        return ret_val

    @classmethod
    def dump_and_scp(cls):
        """
        dump feed(s) using pg_dump
        optionally scp those feeds to servers configured in app.ini [deploy]

        method has command line parser, but method can be called programmatically (w/out command line)
        if now cmdline, then will dump and deploy according to app.ini configured agencies [gtfs] and servers [deploy]
        """

        # step 1: optional cmd-line parser (used to filter either agency and/or server to scp dump file to)
        from ott.utils.parse.cmdline import gtfs_cmdline
        parser = gtfs_cmdline.gtfs_parser(exe_name='bin/gtfsdb_dump_scp', do_parse=False)
        gtfs_cmdline.server_option(parser)
        p = parser.parse_args()

        # step 2: dump feed(s)
        num_dumped = cls.dump(filter=p.agency_id, clean_db=p.clear)

        # step 3: scp feed(s)
        if num_dumped > 0:
            num_scpd = cls.scp(filter=p.server)

        if num_dumped != num_scpd:
            log.warn("There were {} feeds dumped, but only {} feeds were scp'd.".format(num_dumped, num_scpd))

        return num_scpd
