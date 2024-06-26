import argparse
import sys
import os.path
import os
import mechanize  # pip install mechanize
from bs4 import BeautifulSoup as bs  # pip install beautifulsoup4

ldc_catalog_url = "https://catalog.ldc.upenn.edu/"
ldc_login_url = ldc_catalog_url + "login"
ldc_dl_url = ldc_catalog_url + "organization/downloads"


def download(corpus, outdir, suffix, login, password):
    ''' Download an LDC corpus to the specified location '''
    br = mechanize.Browser()
    br.set_handle_robots(False)
    sign_in = br.open(ldc_login_url)
    br.select_form(nr=0)
    br["spree_user[login]"] = login
    br["spree_user[password]"] = password
    logged_in = br.submit()
    dlpage = br.open(ldc_dl_url)
    dlpage = bs(dlpage.read(), 'html.parser')
    dlgroup = {'class': 'button download-counter-button'}

    targetstrs = dlpage.find(id='user-corpora-download-table').findAll(text=corpus)
    options = [x.find_parents()[1] for x in targetstrs]
    # i hate you ldc
    labels = [[y for y in x.children][-2].text.strip().split('\n')[0].strip() for x in options]
    urls = [x.find(attrs=dlgroup).get('href') for x in options]

    if len(options) == 1:
        targeturl = urls[0]
        label = labels[0]
    elif len(options) == 0:
        sys.stderr.write("%s not found\n" % corpus)
        return None
    else:
        choices = [(i, x) for i, x in enumerate(labels)]
        result = None
        while result is None:
            resp = input("choose corpus:\n%s\n >>" % '\n'.join(map(lambda x: "%s=%s" % x, choices)))
            if resp not in map(lambda x: x[0], choices):
                print("Please choose from the available labels")
            else:
                result = resp
        targeturl = urls[int(result)]
        label = labels[int(result)]
    fullurl = ldc_catalog_url + targeturl
    print("Getting " + label)
    destination = os.path.join(outdir, label + "." + suffix)
    result = br.retrieve(fullurl, filename=destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description="Get corpus from LDC: A small script by Jonathan May",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outdir", "-o", help="output directory")
    parser.add_argument("--suffix", "-s", default="tar.gz", help="file suffix")
    parser.add_argument("--corpus", "-c", nargs='+', help="corpus name(s) (e.g. LDC99T42)")
    parser.add_argument("--login", "-l", help="ldc login")
    parser.add_argument("--password", "-p", help="ldc password")

    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    for corpus in args.corpus:
        ofile = os.path.join(args.outdir, corpus + "." + args.suffix)
        result = download(corpus, args.outdir, args.suffix, args.login, args.password)
        if result is not None:
            print("Retrieved %s to %s" % (corpus, result))


if __name__ == '__main__':
    main()
