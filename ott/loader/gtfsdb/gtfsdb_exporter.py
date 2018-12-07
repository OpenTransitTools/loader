from ott.utils import file_utils
from ott.utils import web_utils
from ott.utils import exe_utils
from ott.utils import object_utils
from .gtfsdb_loader import GtfsdbLoader

import os
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

    def export_db_dump(self, server_filter=None, schema_filter=None):
        """
        scp new GTFS db dump files from build server to production servers
        """
        ret_val = True

        def scp_dump_file(server, user, dump_dir, dump_file, server_dir):
            """
            sub-routine to scp gtfsdb dump file to a a given server.
            crazy part of this code is all the path (string) manipulation
            in step 1 below...
            """
            global ret_val

            # step 1: create file paths to dump files locally, and also path where we'll scp these files
            dump_path = os.path.join(dump_dir, dump_file)
            dump_new = file_utils.make_new_path(dump_path)
            dump_svr = file_utils.append_to_path(server_dir, os.path.basename(dump_new), False)

            # step 2: we are going to attempt to scp the dump file over to the server(s)
            #         note: the server paths (e.g., graph_svr, etc...) are relative to the user's home account
            if file_utils.is_min_sized(dump_new):
                scp = None
                try:
                    log.info("scp {} over to {}@{}:{}".format(dump_new, user, server, dump_svr))
                    scp, ssh = web_utils.scp_client(host=server, user=user)
                    scp.put(dump_new, dump_svr)
                except Exception as e:
                    log.warn(e)
                    ret_val = False
                finally:
                    if scp:
                        scp.close()

        # step A: grab config .ini (from app.ini) variables for the server(s) to scp OTP graphs to
        #         note, we need these server(s) to be 'known_hosts'
        user = self.config.get_json('user', section='deploy')
        servers = self.config.get_json('servers', section='deploy')
        gtfsdb_cache = self.config.get_json('gtfsdb_dir', section='deploy')

        # step B: loop thru each server, and scp a graph (and log and jar) to that server
        # import pdb; pdb.set_trace()
        for s in servers:
            if object_utils.is_not_match(server_filter, s):
                continue
            for g in self.graphs:
                if object_utils.is_not_match(graph_filter, g['name']):
                    continue
                dir = otp_utils.config_graph_dir(g, self.this_module_dir)
                svr_dir = file_utils.append_to_path(otp_base_dir, g['name'])
                scp_graph(server=s, user=user, graph_dir=dir, server_dir=svr_dir, graph=g)

        # step C: remove the -new files (so we don't keep deploying / scp-ing)
        for g in self.graphs:
            if object_utils.is_not_match(graph_filter, g['name']):
                continue
            otp_utils.rm_new(graph_dir=g['dir'])

        return ret_val

    @classmethod
    def dump(cls):
        """ export """
        db = GtfsdbLoader()

        # step 1: loop thru all our feeds
        for f in db.feeds:
            db.dump_feed(f)
            # step 2: check date on last export file vs. date of GTFS feed
            # step 3: when export is either older than feed or missing entirely, create a new export and then scp it
