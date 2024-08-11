"""
* pymediawiki.py:
Test of the mediawiki (pymediawiki) to search the GEM wiki.
The mwclient library doesn't have an obvious way to find the URLs of wiki pages,
so I'm using this for that.

For more information:
https://pymediawiki.readthedocs.io/en/latest/quickstart.html
"""

# imports
from mediawiki import MediaWiki

gw = MediaWiki(
    url='https://www.gem.wiki/w/api.php',
    user_agent='sheldon-ramptons-agent'
)

pages = gw.random(pages=3)
print(pages)

pages = gw.opensearch('RENEW Wisconsin', results=1)
print(pages[0][2])
