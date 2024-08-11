"""
mwclient_test.py:
tests the allpages method in the mwclient library for accessing Mediawiki sites via their API.
"""

# imports
import mwclient  # for downloading example Wikipedia articles
import mwparserfromhell  # for splitting Wikipedia articles into sections
import itertools


CATEGORY_TITLE = "Category:Wisconsin"
WIKI_SITE = "www.gem.wiki"
site = mwclient.Site(WIKI_SITE)
pages = site.allpages(limit=100)
for page in itertools.islice(pages, 10000):
# for page in pages[0:100]:
    print(page.name)
