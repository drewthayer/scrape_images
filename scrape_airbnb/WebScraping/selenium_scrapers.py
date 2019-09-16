from selenium import webdriver
from random import randint
from time import sleep
import sys, pdb
import urllib.request

class AirbnbSpider():
    ''' Selenium spider for crawling an Airbnb url '''
    def __init__(self, url, location, image_dir, metadata_file=None, limit=None):
        self.url_to_crawl = url
        self.image_dir = image_dir
        self.location = location
        self.meta_file = metadata_file
        self.limit = limit
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
            # old xpath '//*[contains(@id, "listing")]/div[2]/a'
            listing_divs = self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div/div[2]/div/span/a')
            if self.limit:
                listing_divs = listing_divs[:self.limit]
            urls = []
            for div in listing_divs: # divs are WebElements
                try:
                    #url = div.find_element_by_css_selector('a').get_attribute('href')
                    url = div.get_attribute('href')
                    urls.append(url)
                except Exception as E:
                    print(E)
                    continue
        except Exception as E:
            print(E)
            sys.exit()

        # process urls
        for url in urls:
            print(url)
            listing_id = url.split('/')[-1].split('?')[0]
            # update listings dictionary
            self.listings.update({'{}'.format(id):{'url':url}})
            # process listing
            self.process_listing(url, listing_id)
            self.count += 1


    def process_listing(self, url, listing_id):
        self.driver.get(url)
        # title
        #//*[@id="summary"]/div/div/div[1]/div[1]/div/span/span/h1
        try:
            title = self.driver.find_element_by_xpath('//*[@id="summary"]//h1').text
            print(title)
        except Exception:
            title = ''
            print('no title found')
        # price
        try:
            price = self.driver.find_element_by_class_name('_doc79r').text
            print(price)
        except Exception:
            price = ''
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
            img_id = listing_id + '_' + str(fid)
            # save image
            self.save_image(link, img_id)
            # save metadata
            if self.meta_file:
                newline = f'{img_id},{self.location},{url},{price},{title}\n'
                with open(self.meta_file, 'a') as f:
                    f.write(newline)
                    f.close()
            fid += 1

    def select_image_links(self, links):
        out = []
        for link in links:
            if 'https://' not in link:
                continue
            domain = link.split('//')[1]
            filename = link.split('/')[-1]
            if 'profile' not in filename and 'user' not in filename and 'googleapis' not in domain and 'maps.gstatic' not in domain:
                out.append(link)
        return out

    def save_image(self, url, id):
        urllib.request.urlretrieve(url, self.image_dir + '/' + str(id) + '.png')
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
