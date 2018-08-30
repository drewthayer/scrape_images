# scrape_images
tools for scraping images

### resources

image scraping tutorial:
https://www.pyimagesearch.com/2015/10/12/scraping-images-with-python-and-scrapy/

scrape tools for airbnb:

 - js tool : https://github.com/nonlinearnarrative/scrape-airbnb

 - scrapy blog: https://www.verginer.eu/blog/web-scraping-airbnb/#setting-up-the-system

 - robust, with scrapy-splash, but doesn't quite work: https://github.com/bashedev/airbnb_scraper

 - simpler, works: https://github.com/adodd202/Airbnb_Scraping

 - another project: https://github.com/drewthayer/airbnb-data-collection/blob/master/airbnb.py

 ### using scrapy

 ~~~
 scrapy crawl spider -o results.json
 ~~~

### simple scraping: requests.get()

 it appears that airbnb city pages might not be  scrapable for listing numbers? This file has no listing numbers in it:

 ~~~
r = requests.get(url)
text = r.text
with open('out2.txt','w') as f:
    f.write(text)
 ~~~
