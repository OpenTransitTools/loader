import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'venusian==1.2.0',
    'gtfsdb',
    'ott.gtfsdb_realtime',
    'ott.gbfsdb',
    'ott.osm',
    'ott.utils',
    'psycopg2',
    'mako',
    'scp',
    'paramiko',
    'simplejson',
]

extras_require = dict(
    dev=[],
)


setup(
    name='ott.loader',
    version='0.1.1',
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
        'git+https://github.com/OpenTransitTools/osm.git#egg=ott.osm-0.1.0',
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

        gtfs_update = ott.loader.gtfs.gtfs_cache:main
        gtfs_info = ott.loader.gtfs.gtfs_info:main
        gtfs_fix = ott.loader.gtfs.fix:main
        gtfs_fix_tm = ott.loader.gtfs.fix:rename_trimet_agency

        gtfsdb_load = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.load
        gtfsdb_current_load = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.current_load
        gtfsdb_restore = ott.loader.gtfsdb.gtfsdb_loader:GtfsdbLoader.restore
        gtfsdb_dump = ott.loader.gtfsdb.gtfsdb_exporter:GtfsdbExporter.dump
        gtfsdb_scp = ott.loader.gtfsdb.gtfsdb_exporter:GtfsdbExporter.scp
        gtfsdb_dump_scp = ott.loader.gtfsdb.gtfsdb_exporter:GtfsdbExporter.dump_and_scp

        gtfsrt_load = ott.loader.gtfsdb_realtime.gtfsdb_realtime_loader:GtfsdbRealtimeLoader.load

        otp_restart_new_graphs = ott.loader.otp.graph.otp_runner:OtpRunner.restart_new_graphs
        otp_run = ott.loader.otp.graph.otp_runner:OtpRunner.run
        otp_build = ott.loader.otp.graph.otp_builder:OtpBuilder.build
        otp_export = ott.loader.otp.graph.otp_exporter:OtpExporter.export
        otp_package_new = ott.loader.otp.graph.otp_exporter:OtpExporter.package_new
        otp_v_new = ott.loader.otp.graph.otp_exporter:OtpExporter.otp_v_new
        otp_static_server = ott.loader.otp.graph.otp_runner:OtpRunner.static_server
        otp_preflight = ott.loader.otp.preflight.test_runner:main
        otp_is_up = ott.loader.otp.preflight.test_runner:TestRunner.is_up
        otp_stress_test = ott.loader.otp.preflight.stress.stress_tests:main
        otp_test_urls = ott.loader.otp.preflight.tests_to_urls:main
        otp_version = ott.loader.otp.graph.otp_runner:OtpRunner.version

        sum_update = ott.loader.sum.sum_cache:SumCache.load

        solr_load = ott.loader.solr.solr_loader:SolrLoader.load
        geocoder_tests = ott.loader.geocoder.test:DbExporter.export_all
        geocoder_export_all = ott.loader.geocoder.exporter.db_exporter:DbExporter.export_all
        geocoder_export_routes = ott.loader.geocoder.exporter.routes:Routes.export
        geocoder_export_landmarks = ott.loader.geocoder.exporter.landmarks:Landmarks.export
        geocoder_export_intersections = ott.osm.osm_cache:OsmCache.intersections_cache
        park_ride_export = ott.loader.geocoder.exporter:ParkRideExporter.export


        log_find_pauses = ott.utils.parse.logs.request_dwell:main
        log_count_requests = ott.utils.parse.logs.request_count:main
        log_grep_urls = ott.utils.parse.logs.grep_urls:main
        log_call_urls = ott.utils.parse.logs.call_urls:main
    """,
)
