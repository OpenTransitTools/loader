import os

from ott.utils import otp_utils
from test_suite import ListTestSuites
from test_runner import get_args_parser


def url_args_parser():
    parser = get_args_parser()
    parser.add_argument('--printer',  '-pt',  help="print to stdout rather than a file", action='store_true')
    parser.add_argument('--selenium', '-sel', help="output a selenium IDE file", action='store_true')
    parser.add_argument('--filename', '-f',   help="filename")
    parser.add_argument('--no_place', '-np',  help="use from and to URL params rather than fromPlace & toPlace", action='store_true')
    parser.add_argument('--strip',    '-st',  help="remove strings from a url, ala '?submit&module=planner&'")
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
                # TODO: make this work for other lat beyond 45-parallel
                new_url = new_url\
                    .replace('fromPlace=45.', 'from=FROM::45.') \
                    .replace('toPlace=45.', 'to=TO::45.') \
                    .replace('Place=', '=')

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


def make_filename(args, name, file_path=None, ext=".urls"):
    ''' make .urls file name '''
    filter = ""
    file_name = args.filename if args.filename else name
    if args.test_suite and len(args.test_suite) > 0:
        filter = "-{}".format(args.test_suite)
    file_name = "{}{}{}".format(file_name, filter, ext)

    if file_path:
        file_name = os.path.join(file_path, file_name)

    return file_name


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

        if args.selenium:
            file_name = make_filename(args, name, file_path, ".html")
            selenium(args, file_name, url_list)
        else:
            url_string = '\n'.join(url_list)
            if args.printer:
                print "\n======={}=======\n".format(name)
                print url_string
            else:
                # write urls to file
                file_name = make_filename(args, name, file_path, ".urls")
                with open(file_name, 'w') as f:
                    f.write(url_string)


def selenium(args, file_name, url_list):
    html_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head profile="http://selenium-ide.openqa.org/profiles/test-case">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="selenium.base" href="" />
<title>{0}</title>
</head>
<body>
<table cellpadding="1" cellspacing="1" border="1">
<thead>
<tr><td rowspan="1" colspan="3">{0}</td></tr>
</thead><tbody>
<tr>
    <td>setTimeout</td>
    <td>1500</td>
    <td></td>
</tr>
'''
    html_open = '''
<tr><td>open</td><td>{}</td><td></td></tr>
'''
    html_error_check = '''<tr><td>verifyNotText</td><td>css=div.container &gt; h1</td><td>Error</td></tr>
<tr><td>assertNotTitle</td><td>Exception</td><td></td></tr>
'''
    html_footer = '''
</tbody></table>
</body>
</html>
'''
    # write urls to file
    with open(file_name, 'w') as f:
        h = html_header.format(file_name)
        f.write(h)
        for u in url_list:
            h = html_open.format(u)
            f.write(h)
            f.write(html_error_check)
        f.write(html_footer)


def main():
    parser = url_args_parser()
    args = parser.parse_args()
    printer(args)

if __name__ == '__main__':
    main()

