# Copyright 2011, TriMet
#
# Licensed under the GNU Lesser General Public License 3.0 or any
# later version. See lgpl-3.0.txt for details.
#
import sys
import time

from   ott.loader.osm.rename.osm_abbr_parser import OsmAbbrParser
import ott.loader.osm.rename.pgdb

MAX=999999999999
#MAX=20

class RenameStreets():
    """ Fixup the street labels from various osm streets table(s) in a pgsql database
    """
    limit = MAX
    debug = False

    def __init__(self, street_tables=['transit_segments'], schema=pgdb.dbschema, debug=True, limit=MAX):
        self.debug = debug
        self.limit = limit
        parser = OsmAbbrParser()
        for t in street_tables:
            table = schema + "." + t
            self.add_columns(pgdb.getConnection(), table)
            self.rename_streets(pgdb.getConnection(), table, parser)


    def rename_streets(self, conn, table, parser):
        """ query the database table for osm_name entries, then update the given column with a parsed set of name, prefix, suffix, type, etc...
        """
        cursor = conn.cursor()
        try:
            # step 1 - query database for osm_names/unique row id 
            q = "SELECT  osm_name, id from " + table
            #q += " where osm_name like '%Vet%' " # for testing minimal set of row updates
            if self.debug:
                print q
            cursor.execute(q)

            # step 2a - iterate each row in the database
            c = cursor.rowcount
            k = 0
            rows = cursor.fetchall()
            for rec in rows:
                k+=1
                if k > c or k > self.limit:
                    break         # something strange happened, let's get out of here

                name = rec[0]
                id   = rec[1]

                if name:
                    try:
                        # step 2b - parse the osm_name into its descrete parts
                        data = parser.dict(name)

                        # step 2c - update the given database row 
                        sql  = pgdb.sql_update_str(table, data)
                        sql += " WHERE id=%s"%id
                        cursor.execute(sql)

                        # step 2d - commit things every so often (and write a tic mark to show things still running)
                        if k % 5000 == 0:
                            conn.commit()
                            if self.debug:
                                knum = " {0} of {1} ".format(k, c)
                                sys.stdout.write(knum)
                        elif self.debug and k % 100 == 0:                       
                            sys.stdout.write('.')
                            sys.stdout.flush()                   

                    except Exception, e:
                        print "PARSE EXCEPTION: %s: %s" % (e.__class__.__name__, e)
                        print name, "\n", id, "\n", data, "\n", sql, "\n\n"
                        conn.commit()

        except Exception, e:
            print "SQL EXCEPTION: %s: %s" % (e.__class__.__name__, e)

        # step 3 - cleanup
        conn.commit()
        cursor.close()
        if self.debug:
            print "\nfinished table", table, "\n"


    def add_columns(self, conn, table):
        ''' renames name col in the street tables, and then adds new columns for RLIS like name attributes
            - rename name to osm_name = Southeast Lambert Street
            - name = Lambert
            - prefix = SE
            - suffix = ''
            - type = St
            - label = BOOLEAN
            - label_text = SE Lambert St
        '''
        cursor = conn.cursor()
        try:
            # step 1: rename name to osm_name
            q = "ALTER TABLE " + table + " RENAME name TO osm_name";
            cursor.execute(q)
            if self.debug:
                print q

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
        except:
            if self.debug:
                print "Exception -- can be ignored if the tables already have new columns...  Continuing..."

from ott.utils import num_utils

def main(argv):
    limit = num_utils.to_int(argv[0], MAX)
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
