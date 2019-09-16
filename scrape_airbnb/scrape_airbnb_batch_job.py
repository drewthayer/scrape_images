from selenium import webdriver
from random import randint
from time import sleep
from JsonUtils.write_tools import write_or_update_to_json
import sys, os, pdb, json
import urllib.request
import argparse

from WebScraping.selenium_scrapers import AirbnbSpider

def make_dir(dir_path):
    try:
        os.makedirs(dir_path)
    except FileExistsError as E:
        print(f'exists: {dir_path}')


def construct_search_urls(city, state, country, min_price, max_price, price_delta=10):
    ''' constructs Airbnb search URLs for a city, iterating through price ranges

        inputs:
                city, state, country (strings). 2-word cities are hyphenated e.g. 'Fort-Collins'
                min_price, max_price (int). default price delta = 10

        returns: search urls (list)'''

    # Construct URLs
    URL_frag1 = "https://www.airbnb.com/s/{}--{}--{}/homes?refinement_paths%5B%5D=%2Fhomes&allow_override%5B%5D=&price_max=".format(city, state, country)
    URL_frag2 = "&price_min="
    URL_frag3 = "&s_tag=Dsga8HCj"

    #https://www.airbnb.com/s/tacoma--wa--United-States/homes?refinement_paths%5B%5D=%2Fhomes&current_tab_id=home_tab&selected_tab_id=home_tab&allow_override%5B%5D=&screen_size=large&price_min=100&price_max=110&room_types%5B%5D=Entire%20home%2

    search_urls = []
    for price in range(min_price, max_price, price_delta):
    	search_urls.append(URL_frag1 + str(price + price_delta) + URL_frag2 + str(price) + URL_frag3)

    return search_urls

if __name__=='__main__':
    ''' Selenium webcrawler for scraping Airbnb listings. '''
    # cmd line args
    parser = argparse.ArgumentParser('Selenium webcrawler for scraping Airbnb listings')
    parser.add_argument('-d', dest='out_dir', help='name for output directory w/i this dir')
    #parser.add_argument('--city', dest='city', required=True)
    #parser.add_argument('--state', dest='state', required=True)
    #parser.add_argument('--min_price', dest='min_price', required=True)
    #parser.add_argument('--max_price', dest='max_price', required=True)
    #parser.add_argument('--price_delta', dest='price_delta')
    args = parser.parse_args()

    # search params for batch job
    country = 'United-States'
    city_state_list = [('Des-Moines','IA'),('Tacoma','WA'),('Houston','TX'),('Miami','FL'),
        ('Portland','OR'),('Augusta','ME'),('Atlanta','GA'),('Lexington','KY'),
        ('Tucson','AZ'),('Santa-Fe','NM'),('Arcata','CA'),('Manchester','NH'),
        ('Raleigh','NC'),('Bellingham','WA'),('Cheyenne','WY','Fort-Collins','CO'),
        ('Sacramento','CA'),('Burlington','VT'),('Cleveland','OH'),('Rochester','MN')]

    min_price = 50
    max_price = 300
    price_delta = 25
    limit = 50

    # output locations
    # images, listing urls
    out_dir = os.path.join(os.getcwd(), args.out_dir)
    img_dir = os.path.join(out_dir, 'images')
    listing_dir = os.path.join(out_dir, 'listing-urls')
    [make_dir(x) for x in [img_dir, listing_dir]]

    # queries
    query_logfile = os.path.join(out_dir, 'scrape_queries.txt')
    try:
        with open(query_logfile, 'w') as f:
            f.write('queries\n')
            f.close()
    except Exception as E:
        print(E)

    # listing metadata
    metadata_file = os.path.join(out_dir, 'img_metadata.csv')
    try:
        with open(metadata_file, 'w') as f:
            f.write('img_id,location,url,price,title\n')
            f.close()
    except Exception as E:
        print(E)



    total = 0
    for item in city_state_list:
        city, state = item
        # generate search urls
        search_urls = construct_search_urls(city, state, country, min_price, max_price, price_delta)

        # crawl all urls
        count_total = 0
        for url in search_urls:
            # Run spider
            location = f'{city}_{state}'
            spider = AirbnbSpider(url, location, img_dir, metadata_file, limit=limit)
            output = spider.parse() # saves images to img_dir
            if output:
                # count listings
                listings, count = output
                print('{} listings found'.format(count))

                # write seach query to txt
                with open(query_logfile, 'a+') as f:
                    f.write(f'{url}\n')
                    f.close()

                # write listing ID + url to json
                fname = f'{location}.json'
                write_or_update_to_json(os.path.join(listing_dir, fname), listings)
                count_total += count
            else:
                print(f'url empty: {url}')

        print('\n TOTAL: {} listings found'.format(count_total))