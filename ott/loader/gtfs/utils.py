def get_file_name_from_url(url):
    ret_val = url.split('/')[-1:][0]
    return ret_val

def wget(url, file_name):
    """ wget a file from url
        IMPORTANT NOTE: this will *not* work if the URL is a redirect, etc...
    """
    try:
        # get gtfs file from url
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)

        # write it out
        f = open(file_name, 'w')
        f.write(res.read())
        f.flush()
        f.close()
        res.close()

        logging.info("check_gtfs: downloaded " + url + " into file " + file_name)
    except:
        logging.warn('could not get data from url:\n', url, '\n(not a friendly place)')
