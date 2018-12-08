from ott.utils import file_utils
from ott.utils import web_utils
from ott.utils import exe_utils
from ott.utils.parse.cmdline import gtfs_cmdline

from .gtfsdb_loader import GtfsdbLoader

import logging
log = logging.getLogger(__file__)


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

    def scp_dump_file(self, feed, server, user):
        """
        scp gtfsdb dump file to a a given server.
        crazy part of this code is all the path (string) manipulation
        in step 1 below...
        """
        ret_val = False

        # step 1: create file paths to dump files locally, and also path where we'll scp these files
        feed_name = self.get_feed_name(feed)
        dump_path = self.get_dump_path(feed_name)
        gtfsdb_dir = self.config.get('gtfsdb_dir', section='deploy')

        # step 2: we are going to attempt to scp the dump file over to the server
        #         note: the server paths (e.g., graph_svr, etc...) are relative to the user's home account
        if file_utils.exists(dump_path) and file_utils.is_min_sized(dump_path, 200000):
            scp = None
            try:
                scp, ssh = web_utils.scp_client(host=server, user=user)

                mkdir = "mkdir -p ~/{}".format(gtfsdb_dir)
                log.info("ssh {} on {}@{}".format(mkdir, user, server))
                ssh.exec_command(mkdir)

                log.info("scp {} over to {}@{}:~/{}/".format(dump_path, user, server, gtfsdb_dir))
                scp.put(dump_new, dump_svr)
            except Exception as e:
                log.warn(e)
                ret_val = False
            finally:
                if scp:
                    scp.close()
        return ret_val

    @classmethod
    def dump(cls):
        """
        dump feed(s) using pg_dump
        optionally scp those feeds to servers configured in app.ini [deploy]

        method has command line parser, but method can be called programmatically (w/out command line)
        if now cmdline, then will dump and deploy according to app.ini configured agencies [gtfs] and servers [deploy]
        """
        db = GtfsdbExporter()

        # optional cmd-line parser (used to filter either agency and/or server to scp dump file to)
        parser = gtfs_cmdline.gtfs_parser(do_parse=False)
        gtfs_cmdline.server_option(parser)
        p = parser.parse_args()

        # step 1: loop thru all our feeds
        # import pdb; pdb.set_trace()
        for f in db.feeds:

            # step 2: agency filter
            if p.agency_id:
                agency = p.agency_id.lower()
                if agency != 'all' and agency not in f.get('name').lower():
                    continue

            # step 3: agency not filtered, so dump it
            db.dump_feed(f)

            # step 4: (optionally) scp dump files to prod servers
            if p.server:
                # step 4b: scp filter condition ... don't scp to none or null specified servers via cmdline
                server = p.server.lower()
                if server in ('none', 'null', '0'):
                    continue

                # step 5: loop thru app.ini [deploy] servers, looking to scp the pg_dump file over to production
                user = db.config.get('user', section='deploy')
                for scp_svr in db.config.get_json('servers', section='deploy'):
                    # step 5b: scp filter condition ... either scp to 'all' servers, or a named (via cmdline) server
                    if server == 'all' or server in scp_svr:
                        db.scp_dump_file(f, scp_svr, user)
