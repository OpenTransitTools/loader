import os

from ott.utils import otp_utils
from test_suite import ListTestSuites


def get_args_parser():
    parser = otp_utils.get_initial_arg_parser()
    parser.add_argument('--hostname', '-hn', help="specify the hostname for the test url")
    parser.add_argument('--ws_path',  '-ws', help="OTP url path, ala 'prod' or '/otp/routers/default/plan'")
    parser.add_argument('--printer',  '-p',  help="print to stdout rather than a file", action='store_true')
    parser.add_argument('--filename', '-f',  help="filename")
    parser.add_argument('--no_place', '-np', help="use from and to URL params rather than fromPlace & toPlace", action='store_true')
    parser.add_argument('--strip',    '-st', help="remove strings from a url, ala '?submit&module=planner&'")
    return parser

def to_urls(args, port):
    #import pdb; pdb.set_trace()
    ws_url, map_url = otp_utils.get_test_urls_from_config(hostname=args.hostname, port=port, ws_path=args.ws_path)
    lts = ListTestSuites(ws_url=ws_url, map_url=map_url, filter=args.test_suite)
    urls = lts.to_url_list()

    # fix up the service urls by either removing strings or renaming parameters (fromPlace / toPlace)
    if args.no_place or args.strip:
        fixed_urls = []
        for u in urls:
            new_url = u
            if args.no_place:
                new_url = new_url.replace('Place=', '=')
            if args.strip:
                new_url = new_url.replace(args.strip, '')
            fixed_urls.append(new_url)
        urls = fixed_urls

    return urls


def url_hash_to_list(url_hash):
    ret_val = []
    for key in url_hash:
        url_list = url_hash[key]
        ret_val.extend(url_list)
    return ret_val

def run(args):
    ''' returns a hash table of lists of url strings used in the test suites, ala
        {
          'blah' : ['http://...', 'http://...', ...],
          'glaa' : ['http://...', 'http://...', ...]
        }

        The 'name' for each hash is either the graph name
    '''
    ret_val = {}

    graphs = otp_utils.get_graphs_from_config()
    if args.name == "all":
        for g in graphs:
            urls = to_urls(args, g['port'])
            ret_val[g['name']] = urls
    elif args.name == "none" and args.hostname:
        urls = to_urls(args, "80")
        ret_val[args.hostname] = urls
    else:
        g = otp_utils.find_graph(graphs, args.name)
        if g:
            urls = to_urls(args, g['port'])
            ret_val[args.hostname] = urls
        else:
            print "couldn't find graph {}".format(args.name)
    return ret_val

def printer(args, file_path=None, url_hash=None):
    ''' loop thru a has of URL strings, and write those strings out to either a file or stdout
        @see url_hash format defined by the run() method above.

        NOTE: that args and hash keys go into naming output files
    '''
    if url_hash is None:
        url_hash = run(args)

    for key in url_hash:
        name = key # key to the hash is the file name
        url_list = url_hash[key]
        url_string = '\n'.join(url_list)

        if args.printer:
            print "\n======={}=======\n".format(name)
            print url_string
        else:
            # make .urls file name
            filter = ""
            file_name = args.filename if args.filename else name
            if args.test_suite and len(args.test_suite) > 0:
                filter = "-{}".format(args.test_suite)
            file_name = "{}{}.urls".format(file_name, filter)

            if file_path:
                file_name = os.path.join(file_path, file_name)

            # write urls to file
            with open(file_name, 'w') as f:
                f.write(url_string)


def main():
    parser = get_args_parser()
    args = parser.parse_args()
    printer(args)

if __name__ == '__main__':
    main()

