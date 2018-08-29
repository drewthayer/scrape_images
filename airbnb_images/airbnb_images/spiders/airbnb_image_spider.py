from airbnb_images.items import AirbnbImage
import datetime
import scrapy

class AirbnbImageSpider(scrapy.Spider):
	name = "airbnb_image_spider"
	#allowed_urls = ["https://airbnb.com"]
	start_urls = ["https://www.airbnb.com"]

def parse(self, response):
	# let's only gather Time U.S. magazine covers
    #url = 'https://www.airbnb.com/rooms/521072?location=Denver%2C%20CO%2C%20United%20States&adults=2&guests=1&s=aWMV5CJc'
    url = response.css("div.refineCol ul li").xpath("a[contains(., 'presentation')]")
    yield scrapy.Request(url.xpath("@href").extract_first(), self.parse_image)

def parse_image(self, response):
	# grab the URL of the cover image
	img = response.css(".art-cover-photo figure a img").xpath("@src")
	imageURL = img.extract_first()

	# yield the result
	yield AirbnbImage(file_urls=[imageURL])
