import requests
import bs4
import time
import json
import sys

base_url = 'http://sfbay.craigslist.org'
search_url = '/search/sfc/apa'
index_url = base_url + search_url
results = {}

# Lookup what kind of attr this is
def get_attr_key(attr):
    # print "attr: " + str(attr)
    key = None
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
    print ("."),
    sys.stdout.flush()
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    if len(soup.select('div.mapaddress')) < 1:
        # No map address, skip it
        return

    results[url] = {}

    post_date = soup.time.get_text()
    results[url]['post_date'] = post_date

    price = soup.select('.price')[0].get_text()
    results[url]['price'] = price

    mapaddress = soup.select('div.mapaddress')[0].get_text()
    results[url]['mapaddress'] = mapaddress

    attrs = soup.select('.mapAndAttrs span')
    for attr in attrs:
        attr_text = attr.get_text()
        key = get_attr_key(attr_text)
        if key:
            results[url][key] = attr_text
        # else:
        #     print "Throwing away attr: " + str(attr_text)
    return

def get_index_listing (offset):
    if not offset:
        offset = 0
    url = index_url + '?s=' + str(offset)
    print ("*"),

    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    links = [a.attrs.get('href') for a in soup.select('span.pl a[href^=/]')]

    for i in range (0, len(links)):
        listing_url = base_url + str(links[i])
        # print str(i) + " " + listing_url + "\n"
        get_listing_details(listing_url)

def loop_over_index_listings():
    start = 0
    end = 100 # 2500
    step = 100
    for i in xrange(start, end, step):
        # print i
        get_index_listing(i)
        time.sleep(5)

def main():
    loop_over_index_listings()

main()
# get_listing_details('http://sfbay.craigslist.org//sfc/apa/5126515369.html')
# get_listing_details('http://sfbay.craigslist.org/sfc/apa/5134263639.html') # No map
print json.dumps(results)