import bs4
from collections import defaultdict
import json
import requests
import sys
import time
import urllib.parse as urlparse


BASE_URL = 'https://sfbay.craigslist.org'
BASE_LISTING_PATH = '/sfc/apa'
FILTER = '?nh=3&availabilityMode=0&sale_date=all+dates'
# FILTER = ''
SEARCH_URL = '/search'
INDEX_URL = BASE_URL + SEARCH_URL + BASE_LISTING_PATH + FILTER
MATCH_URL = BASE_URL + BASE_LISTING_PATH

results = {}

# Lookup what kind of attr this is
def get_attr_key(attr):
    # print("attr: " + str(attr))
    housing_types = ['apartment', 'house', 'flat','condo', 'duplex', 'in-law', 'loft']
    if attr.lower() in housing_types:
        return 'housing_type'

    laundry_types = "laundry in bldg w/d in unit no laundry on site w/d hookups"
    if attr.lower() in laundry_types:
        return 'laundry_type'

    if ("parking" in attr.lower()) or \
        ("garage" in attr.lower()) or \
        ("carport" in attr.lower()):
        return'parking_type'

    if "BR" in attr:
        return 'room_count'

    if "ft2" in attr.lower():
        return 'size_sqft'

    if "smoking" in attr.lower():
        return "smoking"

    if "cats" in attr.lower():
        return "cats"

    if "dogs" in attr.lower():
        return "dogs"

    if "furnished" in attr.lower():
        return "furnished"

    if "available" in attr.lower():
        return "availability"

    if "wheelchair accessible" in attr.lower():
        return "ada"

def get_listing_details(url):
    sys.stdout.flush()
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # if len(soup.select('div.mapaddress')) < 1:
    #     # No map address, skip it
    #     return

    results[url] = {}

    if soup.time:
        post_date = soup.time.get_text()
        results[url]['post_date'] = post_date.strip()

    price = soup.select('.price')[0].get_text()
    results[url]['price'] = price

    try:
        mapaddress = soup.select('div.mapaddress')[0].get_text()
        results[url]['mapaddress'] = mapaddress
    except IndexError:
        pass

    attrs = soup.select('.mapAndAttrs span')
    for attr in attrs:
        attr_text = attr.get_text()
        key = get_attr_key(attr_text)
        if key:
            results[url][key] = attr_text
        else:
            print("Throwing away attr: %s" % (str(attr_text)))
    return

def get_index_listing(offset):
    if not offset:
        offset = 0

    url = INDEX_URL
    if offset:
        if list(urlparse.urlparse(url))[4]:
            url += '&'
        else:
            url += '?'
        url += 's=%s' % str(offset)

    print('Fetching index: %s' % url)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    # print(soup)

    i = 0
    print(BASE_URL)
    listing_map = defaultdict(bool)
    for link in soup.find_all('a', href=True):
        listing_url = link['href']
        if MATCH_URL in listing_url:
            if not listing_map[listing_url]:
                print("listing %s: %s" % (str(i), listing_url))
                get_listing_details(listing_url)
                listing_map[listing_url] = True
                i += 1

def loop_over_index_listings():
    listings_per_page = 120

    page_start = 0
    page_end = 2 # 2500 max
    for i in range(page_start, page_end):
        print("Getting index page %s" % str(i))
        get_index_listing(i * listings_per_page)
        # time.sleep(5)

def main():
    loop_over_index_listings()


main()
print(json.dumps(results))
