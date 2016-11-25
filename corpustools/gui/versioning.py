from pkg_resources import parse_version
from urllib.request import urlopen
from urllib.parse import quote
import re

import corpustools

VERSION = corpustools.__version__

def open_url(url):
    f = urlopen(url, timeout=30)
    try:
        size = f.headers.get("content-length",None)
        if size is not None:
            size = int(size)
    except ValueError:
        pass
    else:
        f.size = size
    return f

def join_app_version(appname,version,platform):
    """Join an app name, version and platform into a version directory name.
    For example, ("app-name","0.1.2","win32") => appname-0.1.2.win32
    """
    return "%s-%s.%s" % (appname,version,platform,)

def find_versions(download_url):
    version_re = "[a-zA-Z0-9\\.-_]+"
    appname_re = "(?P<version>%s)" % (version_re,)
    name_re = "(%s|%s)" % ("PhonologicalCorpusTools", quote("PhonologicalCorpusTools"))
    appname_re = join_app_version(name_re,appname_re,"win-amd64")
    filename_re = "%s\\.(zip|exe|from-(?P<from_version>%s)\\.patch)"
    filename_re = filename_re % (appname_re,version_re,)
    link_re = "href=['\"]?(?P<href>([^'\"]*/)?%s)['\"]?" % (filename_re,)

    df = open_url(download_url)

    try:
        downloads = df.read().decode("utf-8-sig")
    finally:
        df.close()
    versions = list()
    for match in re.finditer(link_re,downloads,re.I):
        version = match.group("version")
        href = match.group("href")
        from_version = match.group("from_version")
        versions.append(version)
    return versions
