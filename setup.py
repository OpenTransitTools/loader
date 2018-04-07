import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'gtfsdb',
    'ott.gtfsdb_realtime',
    'ott.utils',
    'ott.gbfsdb',
    'psycopg2',
    'mako',
    'scp',
    'paramiko == 1.14.2',
    'simplejson',
    'osmread',    # a lot of dependant libs needed for OSM (pyparsing, protobuf, shapely)
    'protobuf',
    'pyparsing',
    'shapely',
]

# sys dependant dependencies
if sys.platform == "darwin" or "win" not in sys.platform:
    requires.append('imposm')

# eggs that you need if you're running a version of python lower than 2.7
if sys.version_info[:2] < (2, 7):
    requires.extend(['argparse>=1.2.1', 'unittest2>=0.5.1'])


extras_require = dict(
    dev=[],
)


setup(
    name='ott.loader',
    version='0.1.0',
    description='Open Transit Tools - OTT Loader',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    dependency_links=[
        'git+https://github.com/OpenTransitTools/utils.git#egg=ott.utils-0.1.0',
        'git+https://github.com/OpenTransitTools/gbfsdb.git#egg=ott.gbfsdb-1.0.0',
        'git+https://github.com/OpenTransitTools/gtfsdb.git#egg=gtfsdb-1.0.0',
        'git+https://github.com/OpenTransitTools/gtfsdb_realtime.git#egg=ott.gtfsdb_realtime-1.0.0',
    ],
    license="Mozilla-derived (http://opentransittools.com)",
    url='http://opentransittools.com',
    keywords='ott, osm, otp, gtfs, gtfsdb, data, database, services, transit',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=requires,
    test_suite="ott.loader.tests",
    # find ott | grep py$ | xargs grep "def.main"
    entry_points="""
        [console_scripts]
        download_data = ott.loader.loader:download_data
        load_all = ott.loader.loader:load_all
        load_and_export = ott.loader.loader:load_and_export
        export_all = ott.loader.loader:export_all

        osm_update = ott.loader.osm.osm_cache:OsmCache.load
        osm_to_pbf = ott.loader.osm.osm_cache:OsmCache.convert_osm_to_pbf
        pbf_to_osm = ott.loader.osm.osm_cache:OsmCache.convert_pbf_to_osm
        osm_other_exports = ott.loader.osm.osm_cache:OsmCache.other_exports
        osm_stats = ott.loader.osm.osm_info:OsmInfo.print_stats
        osm_rename = ott.loader.osm.osm_rename:main
        osm_intersections = ott.loader.osm.intersections.osm_to_intersections:main

        gtfs_update = ott.loader.gtfs.gtfs_cache:main
        gtfs_info = ott.loader.gtfs.info:main
        gtfs_fix = ott.loader.gtfs.fix:main
        gtfs_fix_tm = ott.loader.gtfs.fix:rename_trimet_agency

        gtfsdb_load = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.load
        gtfsdb_dump = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.dump
        gtfsdb_restore = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.restore
        gtfsdb_rt_load = ott.loader.gtfsdb_realtime.gtfsdb_realtime_loader:GtfsdbRealtimeLoader.load

        otp_restart_new_graphs = ott.loader.otp.graph.otp_runner:OtpRunner.restart_new_graphs
        otp_run = ott.loader.otp.graph.otp_runner:OtpRunner.run
        otp_build = ott.loader.otp.graph.otp_builder:OtpBuilder.build
        otp_export = ott.loader.otp.graph.otp_exporter:OtpExporter.export
        otp_package_new = ott.loader.otp.graph.otp_exporter:OtpExporter.package_new
        otp_static_server = ott.loader.otp.graph.otp_runner:OtpRunner.static_server
        otp_preflight = ott.loader.otp.preflight.test_runner:main
        otp_stress_test = ott.loader.otp.preflight.stress.stress_tests:main
        otp_test_urls = ott.loader.otp.preflight.tests_to_urls:main

        sum_update = ott.loader.sum.sum_cache:SumCache.load

        geocoder_tests = ott.loader.geocoder.test:DbExporter.export_all
        geocoder_export_all = ott.loader.geocoder.db_export.db_exporter:DbExporter.export_all
        geocoder_export_landmarks = ott.loader.geocoder.db_export.landmarks:Landmarks.export
        geocoder_export_intersections = ott.loader.geocoder.db_export.intersections:Intersections.export
        solr_load = ott.loader.solr.solr_loader:SolrLoader.load

        log_find_pauses = ott.utils.parse.logs.request_dwell:main
        log_count_requests = ott.utils.parse.logs.request_count:main
        log_grep_urls = ott.utils.parse.logs.grep_urls:main
        log_call_urls = ott.utils.parse.logs.call_urls:main
    """,
)
