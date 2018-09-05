from selenium import webdriver
from random import randint
from time import sleep
from pyvirtualdisplay import Display

class AirbnbSpider():
    def __init__(self):
        self.url_to_crawl = "https://www.airbnb.com/s/Denver--CO--United-States/homes"
        self.items = []

        # Open headless chromedriver
    def start_driver(self):
        print('starting driver...')
        #self.display = Display(visible=0, size=(800, 600))
        #self.display.start()
        self.driver = webdriver.Chrome()
        sleep(4)

    # Close chromedriver
    def close_driver(self):
        print('closing driver...')
        #self.display.stop()
        self.driver.quit()
        print('closed!')

    # Tell the browser to get a page
    def get_page(self, url):
        print('getting page...')
        self.driver.get(url)
        sleep(randint(2,3))

    	# Munchery front gate page
    def get_urls(self):
        print('getting listing urls...')
        try:
            #for div in self.driver.find_elements_by_xpath('//*[@class="_1mpo9ida")]//href'):
            for div in self.driver.find_elements_by_xpath('//*[contains(@id, "listing")]/div[2]/a'):
                data = div.text
                print(data)
                if data:
                    self.items.append(data)
                else:
                    pass

        except Exception:
            pass

    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.get_urls()
        #self.grab_list_items()
        self.close_driver()

        if self.items:
            return self.items
        else:
            return False, False


if __name__=='__main__':
    # Run spider
    airbnb = AirbnbSpider()
    items_list = airbnb.parse()

	# def grab_list_items(self):
	# 	print('grabbing list of items...')
	# 	for div in self.driver.find_elements_by_xpath('//ul[@class="menu-items row"]//li'):
	# 		data = self.process_elements(div)
	# 		if data:
	# 			self.all_items.append(data)
	# 		else:
	# 			pass
