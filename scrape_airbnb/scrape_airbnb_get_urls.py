from selenium import webdriver
from random import randint
from time import sleep
from JsonUtils.write_tools import write_or_update_to_json
import sys

class AirbnbSpider():
    def __init__(self, url):
        self.url_to_crawl = url
        #self.url_to_crawl = "https://www.airbnb.com/s/Denver--CO--United-States/homes"
        self.listings = {}

        # Open headless chromedriver
    def start_driver(self):
        print('starting driver...')
        self.driver = webdriver.Chrome()
        sleep(4)

    # Close chromedriver
    def close_driver(self):
        print('closing driver...')
        self.driver.quit()
        print('driver closed')

    # Tell the browser to get a page
    def get_page(self, url):
        print('getting page...')
        self.driver.get(url)
        sleep(randint(2,3))

    	# Munchery front gate page
    def get_listings(self):
        print('getting listing urls...')
        try:
            #for div in self.driver.find_elements_by_xpath('//*[@class="_1mpo9ida")]//href'):
            self.count = 0
            for div in self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div[2]/a'):
                metadata = div.text
                url = div.get_attribute('href')
                id = url.split('/')[-1].split('?')[0]
                print(metadata)
                print(url)
                if metadata:
                    self.listings.update({'{}'.format(id):{'url':url, 'metadata':metadata}})
                else:
                    pass
                self.count += 1

        except Exception:
            pass

    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_listings()
        #self.grab_list_items()
        self.close_driver()

        if self.listings:
            return self.listings, self.count
        else:
            return False

def construct_search_urls(city, state, country, min_price, max_price):
    # Construct URLs
    URL_frag1 = "https://www.airbnb.com/s/{}--{}--{}/homes?refinement_paths%5B%5D=%2Fhomes&allow_override%5B%5D=&price_max=".format(city, state, country)
    URL_frag2 = "&price_min="
    URL_frag3 = "&s_tag=Dsga8HCj"

    search_urls = []
    for price in range(min_price, max_price, 10):
    	search_urls.append(URL_frag1 + str(price+10) + URL_frag2 + str(price) + URL_frag3)

    return search_urls


if __name__=='__main__':
    # cmd line args
    city = sys.argv[1]      # e.g. 'Denver'
    state = sys.argv[2]     # e.g. 'CO'
    # search params
    country = 'United-States'
    min_price = 50
    max_price = 200

    # output directory
    results_dir = 'listings'

    # generate search urls
    search_urls = construct_search_urls(city, state, country, min_price, max_price)

    # crawl all urls
    count_total = 0
    for url in search_urls:
        # Run spider
        spider = AirbnbSpider(url)
        listings, count = spider.parse()
        print('{} listings found'.format(count))

        #write to json
        fname = 'airbnb_{}_{}.json'.format(city, state)
        write_or_update_to_json(results_dir + '/' + fname, listings)
        count_total += count

    print('\n TOTAL: {} listings found'.format(count_total))
