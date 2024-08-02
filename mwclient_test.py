# https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search

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
