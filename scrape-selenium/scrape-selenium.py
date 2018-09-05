from selenium import webdriver
from random import randint
from time import sleep
import json

class AirbnbSpider():
    def __init__(self, city, state, country):
        self.url_to_crawl = "https://www.airbnb.com/s/{}--{}--{}/homes".format(city, state, country)
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
        print('closed!')

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

        except Exception:
            pass

    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_listings()
        #self.grab_list_items()
        self.close_driver()

        if self.listings:
            return self.listings
        else:
            return False, False


if __name__=='__main__':
    # search params
    city='Rollins'
    state='MO'
    country='United-States'
    # Run spider
    airbnb = AirbnbSpider(city, state, country)
    listings = airbnb.parse()

    # write to json
    dir = 'listing_urls'
    fname = 'airbnb_{}_{}.json'.format(city, state)
    with open(dir + '/' + fname, 'w') as f:
        json.dump(listings, f)
