"""
  Copyright 2011, TriMet
  Licensed under the GNU Lesser General Public License 3.0 or any later version. See lgpl-3.0.txt for details.
"""
import sys
import time

from . import pgdb
from .osm_abbr_parser import OsmAbbrParser

from ott.utils import num_utils

import logging
logging.basicConfig(level=logging.INFO)

MAX=999999999999
#MAX=20


class RenameStreets():
    """
    Fixup the street labels from various osm streets table(s) in a pgsql database
    """
    limit = MAX
    parser = None

    def __init__(self, street_tables=['transit_segments'], schema=pgdb.dbschema, limit=MAX):
        self.limit = limit
        self.parser = OsmAbbrParser()
        for t in street_tables:
            table = schema + "." + t
            self.add_columns(table)
            self.rename_streets(table)

    def rename_streets(self, table):
        """
        query the database table for osm_name entries, then update the given column with a parsed set of name, prefix, suffix, type, etc...
        """
        #import pdb; pdb.set_trace()
        try:
            # step 0: database connect
            conn = pgdb.getConnection()
            cursor = conn.cursor()

            # step 1 - query database for osm_names/unique row id
            q = "SELECT  osm_name, id from " + table
            #q += " where osm_name like '%Vet%' " # for testing minimal set of row updates
            logging.info(q)
            cursor.execute(q)

            # step 2a - iterate each row in the database
            c = cursor.rowcount
            k = 0
            rows = cursor.fetchall()
            for rec in rows:
                if k > c or k > self.limit:
                    break         # something strange happened, let's get out of here

                name = rec[0]
                id   = rec[1]
                if name:
                    k+=1
                    try:
                        # step 2b - parse the osm_name into its discrete parts
                        data = self.parser.dict(name)

                        # step 2c - update the given database row 
                        sql  = pgdb.sql_update_str(table, data)
                        sql += " WHERE id=%s"%id
                        cursor.execute(sql)

                        # step 2d - commit things every so often (and write a tic mark to show things still running)
                        if k % 5000 == 0:
                            conn.commit()
                            logging.warn(" {0} of {1} ".format(k, c))
                    except Exception, e:
                        conn.commit()
                        logging.info(e)

            # step 3 - cleanup
            conn.commit()
            cursor.close()
            conn.close()
            cursor = None
            conn = None
            logging.info("\nfinished table {}\n".format(table))
        except Exception, e:
            logging.error(e)


    def add_columns(self, table):
        """ renames name col in the street tables, and then adds new columns for RLIS like name attributes
            - rename name to osm_name = Southeast Lambert Street
            - name = Lambert
            - prefix = SE
            - suffix = ''
            - type = St
            - label = BOOLEAN
            - label_text = SE Lambert St
        """
        try:
            # step 0: database connect
            conn = pgdb.getConnection()
            cursor = conn.cursor()

            # step 1: rename name to osm_name
            q = "ALTER TABLE " + table + " RENAME name TO osm_name";
            cursor.execute(q)
            logging.info(q)

            # step 2: new text columns
            new_cols = ('name', 'prefix', 'suffix', 'type', 'label_text')
            for c in new_cols:
                q = "ALTER TABLE " + table + " ADD " + c + " TEXT";
                cursor.execute(q)

            # step 3: other columns
            q = "ALTER TABLE " + table + " ADD label BOOLEAN";
            cursor.execute(q)

            # step 4: commit
            conn.commit()
            cursor.close()
            conn.close()
            cursor = None
            conn = None
        except Exception, e:
            logging.debug(e)
            logging.debug("Exception -- can be ignored if the tables already have new columns...  Continuing...")


def main(argv):
    limit = num_utils.array_item_to_int(argv, 1, MAX)
    if "carto":
        RenameStreets(('_line', '_roads'), 'osmcarto', limit=limit)
    else:
        RenameStreets(limit=limit)


def profile_run(argv):
    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()
    main(argv)
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


def timed_run(argv):
    start_seconds = time.time()
    start_time = time.localtime()
    print time.strftime('begin time: %H:%M:%S', start_time)
    main(argv)
    end_time = time.localtime()
    print time.strftime('end time: %H:%M:%S', end_time)
    process_time = time.time() - start_seconds
    print 'processing time: %.0f seconds' %(process_time)


if __name__ == '__main__':
    #profile_run(sys.argv)
    timed_run(sys.argv)
