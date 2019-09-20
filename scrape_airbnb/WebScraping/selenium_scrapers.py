from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from random import randint
from time import sleep
import sys, logging, json, os, csv, pdb
import urllib.request

logging.basicConfig(format='%(asctime)s - %(funcName)s - %(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',level=logging.INFO)
logger = logging.getLogger(__name__)

class AirbnbSpider():
    ''' Selenium spider for crawling an Airbnb url '''
    def __init__(self, url, location, image_dir, metadata_file=None, limit=None, pricerange=None, photo_size='large'):
        self.url_to_crawl = url
        self.image_dir = image_dir
        self.location = location
        self.meta_file = metadata_file
        self.limit = limit
        self.pricerange = pricerange # string
        self.photo_size = photo_size # currently not necessary, have to scrape at .jpg endpoint
        self.listings = {}
        self.listing_count = 0
        self.img_count = 0

        #if self.meta_file: This was re-writing it every time
            #self.csv_writer = csv.writer(open(self.meta_file, 'w+'), delimiter=',')
        #else:
        #       self.csv_writer = None


    # Open headless chromedriver
    def start_driver(self):
        logger.debug('starting driver...')
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        sleep(4)


    # Close chromedriver
    def close_driver(self):
        logger.debug('closing driver...')
        self.driver.quit()
        print('driver closed')


    # Tell the browser to get a page
    def get_page(self, url):
        logger.debug('getting page...')
        self.driver.get(url)
        sleep(randint(2,3))


    # Get listing URLs on a page
    def get_listings_from_page(self):
        logger.debug('getting listing urls...')
        try:
            # save listing url and metadata
            # old xpath '//*[contains(@id, "listing")]/div[2]/a'
            listing_divs = self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div/div[2]/div/span/a')
            logger.info(f'{len(listing_divs)} listings found, limit = {self.limit}')
            if self.limit:
                listing_divs = listing_divs[:self.limit]
            urls = []
            for div in listing_divs: # divs are WebElements
                try:
                    #url = div.find_element_by_css_selector('a').get_attribute('href')
                    url = div.get_attribute('href')
                    urls.append(url)
                except Exception as E:
                    logger.error(f'ERROR: {E}')
                    continue
        except Exception as E:
            logger.error(f'ERROR: {E}')
            sys.exit()

        # process urls
        for url in urls:
            logger.debug(url)
            listing_id = url.split('/')[-1].split('?')[0]
            # update listings dictionary
            self.listings.update({'{}'.format(id):{'url':url}})
            # process listing
            self.process_listing(url, listing_id)
            self.listing_count += 1

    def get_soup_from_url(self):
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def find_scripts(self,soup,idx):
        scripts = soup.find_all('script', type='application/json')
        return self.clean_script_text(scripts[idx].text)

    def clean_script_text(self,text):
        i_start = text.find('{')
        i_end = text.rfind('}') + 1
        return text[i_start:i_end]

    def download_photo(self,url,fname):
        urllib.request.urlretrieve(url, fname)

    def get_price(self):
        price = None
        try:
            price = self.driver.find_element_by_class_name('_doc79r').text
            logger.debug(price)
        except Exception:
            logger.debug('no price found')

        return price

    def process_listing(self, url, listing_id):
        self.driver.get(url)
        soup = self.get_soup_from_url()
        text = self.find_scripts(soup,idx=3)
        data = json.loads(text)
        price = self.get_price()
        listing_data = data['bootstrapData']['reduxData']['homePDP']['listingInfo']['listing']
        photos = listing_data['webPListingPhotos']
        fid = 1
        for photo in photos:
            img_id = f'{listing_data["id"]}_' + str(fid).zfill(2)
            filename = os.path.join(self.image_dir, img_id + '.png')
            img_url = photo[self.photo_size].split('.jpg')[0]+'.jpg'
            self.download_photo(img_url,filename)
            fid += 1

            # save metadata
            if self.meta_file: # can't find price or title for now
                caption = photo["caption"].replace(',',';')
                price = price if price else ''
                newline = f'{img_id},{caption},{price},{self.pricerange},{self.location},{img_url}\n' # sometimes caption has commas...
                #newline = [img_id, photo["caption"], self.location, img_url]
                #self.csv_writer.writerow(newline)
                #pdb.set_trace()
                with open(self.meta_file, 'a') as f:
                    f.write(newline)
                    f.close()


        # title
        #//*[@id="summary"]/div/div/div[1]/div[1]/div/span/span/h1
        # try:
        #     title = self.driver.find_element_by_xpath('//*[@id="summary"]//h1').text
        #     logger.debug(title)
        # except Exception:
        #     title = ''
        #     logger.debug('no title found')
        # # price
        # try:
        #     price = self.driver.find_element_by_class_name('_doc79r').text
        #     logger.debug(price)
        # except Exception:
        #     price = ''
        #     logger.debug('no price found')
        #
        # # elements with images
        # img_elements = self.driver.find_elements_by_xpath('//*[@id="room"]//img')
        #
        # # extract 'src' link from elements
        # all_img_links = [x.get_attribute('src') for x in img_elements]
        #
        # # select only links with house images
        # img_links = self.select_image_links(all_img_links)
        # if len(img_links) > 0:
        #     # save images from links, sequentially named
        #     fid = 1
        #     for link in img_links:
        #         img_id = listing_id + '_' + str(fid)
        #         # save image
        #         self.save_image(link, img_id)
        #         self.img_count += 1
        #         # save metadata
        #         if self.meta_file:
        #             newline = f'{img_id},{self.location},{url},{price},{title}\n'
        #             with open(self.meta_file, 'a') as f:
        #                 f.write(newline)
        #                 f.close()
        #         fid += 1
        # else:
        #     logger.info('no images found')


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


    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_listings_from_page()
        self.close_driver()

        if self.listings:
            return self.listings, self.listing_count, self.img_count
        else:
            logger.info('No listings found')
            return False

################################################################################

class AirbnbSpider_v1():
    ''' Selenium spider for crawling an Airbnb url '''
    def __init__(self, url, location, image_dir, metadata_file=None, limit=None):
        self.url_to_crawl = url
        self.image_dir = image_dir
        self.location = location
        self.meta_file = metadata_file
        self.limit = limit
        self.listings = {}
        self.listing_count = 0
        self.img_count = 0


    # Open headless chromedriver
    def start_driver(self):
        logger.debug('starting driver...')
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        sleep(4)


    # Close chromedriver
    def close_driver(self):
        logger.debug('closing driver...')
        self.driver.quit()
        print('driver closed')


    # Tell the browser to get a page
    def get_page(self, url):
        logger.debug('getting page...')
        self.driver.get(url)
        sleep(randint(2,3))


    # Get listing URLs on a page
    def get_listings_from_page(self):
        logger.debug('getting listing urls...')
        try:
            # save listing url and metadata
            # old xpath '//*[contains(@id, "listing")]/div[2]/a'
            listing_divs = self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div/div[2]/div/span/a')
            logger.info(f'{len(listing_divs)} listings found, limit = {self.limit}')
            if self.limit:
                listing_divs = listing_divs[:self.limit]
            urls = []
            for div in listing_divs: # divs are WebElements
                try:
                    #url = div.find_element_by_css_selector('a').get_attribute('href')
                    url = div.get_attribute('href')
                    urls.append(url)
                except Exception as E:
                    logger.error(f'ERROR: {E}')
                    continue
        except Exception as E:
            logger.error(f'ERROR: {E}')
            sys.exit()

        # process urls
        for url in urls:
            logger.info(url)
            listing_id = url.split('/')[-1].split('?')[0]
            # update listings dictionary
            self.listings.update({'{}'.format(id):{'url':url}})
            # process listing
            self.process_listing(url, listing_id)
            self.listing_count += 1


    def process_listing(self, url, listing_id):
        self.driver.get(url)
        # title
        #//*[@id="summary"]/div/div/div[1]/div[1]/div/span/span/h1
        try:
            title = self.driver.find_element_by_xpath('//*[@id="summary"]//h1').text
            logger.debug(title)
        except Exception:
            title = ''
            logger.debug('no title found')
        # price
        try:
            price = self.driver.find_element_by_class_name('_doc79r').text
            logger.debug(price)
        except Exception:
            price = ''
            logger.debug('no price found')

        # elements with images
        img_elements = self.driver.find_elements_by_xpath('//*[@id="room"]//img')

        # extract 'src' link from elements
        all_img_links = [x.get_attribute('src') for x in img_elements]

        # select only links with house images
        img_links = self.select_image_links(all_img_links)
        if len(img_links) > 0:
            # save images from links, sequentially named
            fid = 1
            for link in img_links:
                img_id = listing_id + '_' + str(fid)
                # save image
                self.save_image(link, img_id)
                self.img_count += 1
                # save metadata
                if self.meta_file:
                    newline = f'{img_id},{self.location},{url},{price},{title}\n'
                    with open(self.meta_file, 'a') as f:
                        f.write(newline)
                        f.close()
                fid += 1
        else:
            logger.info('no images found')


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


    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_listings_from_page()
        self.close_driver()

        if self.listings:
            return self.listings, self.listing_count, self.img_count
        else:
            logger.info('No listings found')
            return False
