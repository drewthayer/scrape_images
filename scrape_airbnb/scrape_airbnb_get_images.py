from selenium import webdriver
from random import randint
from time import sleep
from JsonUtils.write_tools import write_or_update_to_json
import sys
import urllib.request

class AirbnbSpider():
    ''' Selenium spider for crawling an Airbnb url '''
    def __init__(self, url, image_dir):
        self.url_to_crawl = url
        self.image_dir = image_dir
        #self.url_to_crawl = "https://www.airbnb.com/s/Denver--CO--United-States/homes"
        self.listings = {}
        self.count = 0

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

    # Get listing URLs on a page
    def get_listings_from_page(self):
        print('getting listing urls...')
        try:
            # save listing url and metadata
            listing_divs = self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div[2]/a')
            urls = [div.get_attribute('href') for div in listing_divs] # divs are WebElements
        except Exception:
            pass

        # process urls
        for url in urls:
            print(url)
            id = url.split('/')[-1].split('?')[0]
            # update json
            self.listings.update({'{}'.format(id):{'url':url}})
            # process listing
            self.process_listing(url, id)
            self.count += 1


    def process_listing(self, url, id):
        self.driver.get(url)
        # title
        #//*[@id="summary"]/div/div/div[1]/div[1]/div/span/span/h1
        try:
            title = self.driver.find_element_by_xpath('//*[@id="summary"]//h1').text
            print(title)
        except Exception:
            print('no title found')
        # price
        try:
            price = self.driver.find_element_by_class_name('_doc79r').text
            print(price)
        except Exception:
            print('no price found')

        # elements with images
        img_elements = self.driver.find_elements_by_xpath('//*[@id="room"]//img')

        # extract 'src' link from elements
        all_img_links = [x.get_attribute('src') for x in img_elements]

        # select only links with house images
        img_links = self.select_image_links(all_img_links)

        # save images from links, sequentially named
        fid = 1
        for link in img_links:
            self.save_image(link, id, fid)
            fid += 1

    def select_image_links(self, links):
        out = []
        for link in links:
            domain = link.split('//')[1]
            filename = link.split('/')[-1]
            if 'profile' not in filename and 'user' not in filename and 'googleapis' not in domain:
                out.append(link)
        return out

    def save_image(self, url, name, fid):
        fname = name + '_' + str(fid)
        urllib.request.urlretrieve(url, self.image_dir + '/' + fname + '.png')
        print('image saved')

    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_listings_from_page()
        self.close_driver()

        if self.listings:
            return self.listings, self.count
        else:
            return False


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

    search_urls = []
    for price in range(min_price, max_price, price_delta):
    	search_urls.append(URL_frag1 + str(price+10) + URL_frag2 + str(price) + URL_frag3)

    return search_urls


if __name__=='__main__':
    ''' Selenium webcrawler for scraping Airbnb listings. '''
    # cmd line args
    city = sys.argv[1]      # e.g. 'Denver'
    state = sys.argv[2]     # e.g. 'CO'

    # search params
    country = 'United-States'
    min_price = 50
    max_price = 200

    # output directories
    results_dir = 'Listings'
    image_dir = 'Images_from_listings_2'

    # generate search urls
    search_urls = construct_search_urls(city, state, country, min_price, max_price)

    # crawl all urls
    count_total = 0
    for url in search_urls:
        # Run spider
        spider = AirbnbSpider(url, image_dir)
        listings, count = spider.parse()
        print('{} listings found'.format(count))

        #write to json
        fname = 'airbnb_{}_{}.json'.format(city, state)
        write_or_update_to_json(results_dir + '/' + fname, listings)
        count_total += count

    print('\n TOTAL: {} listings found'.format(count_total))
