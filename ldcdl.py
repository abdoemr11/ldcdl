#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2016, Jonathan May

import argparse
import sys
import os.path
import os
import mechanize # pip install mechanize
from bs4 import BeautifulSoup as bs # pip install beautifulsoup4

ldc_catalog_url="https://catalog.ldc.upenn.edu/"
ldc_login_url=ldc_catalog_url+"login"
ldc_dl_url=ldc_catalog_url+"organization/downloads"

def download(corpus, destination, login, password):
  ''' Download an LDC corpus to the specified location '''
  br = mechanize.Browser()
  br.set_handle_robots(False)
  sign_in = br.open(ldc_login_url)
  br.select_form(nr = 0)
  br["spree_user[login]"]=login
  br["spree_user[password]"]=password
  logged_in=br.submit()
  dlpage = br.open(ldc_dl_url)
  dlpage = bs(dlpage.read(), 'html.parser')

  targetstr = dlpage.find(id='user-corpora-download-table').find(text=corpus)
  dlgroup = {'class':'button download-counter-button'}
  targeturl = targetstr.fetchParents()[1].find(attrs=dlgroup).get('href')
  fullurl=ldc_catalog_url+targeturl
  result = br.retrieve(fullurl, filename=destination)
  return result[0]

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
  except IOError, msg:
    parser.error(str(msg))

  for corpus in args.corpus:
    ofile = os.path.join(args.outdir, corpus+"."+args.suffix)
    result = download(corpus, ofile, args.login, args.password)
    print("Retrieved %s to %s" % (corpus, ofile))



if __name__ == '__main__':
  main()
