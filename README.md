# scrape_images
tools for scraping images

### resources

image scraping tutorials:

https://www.pyimagesearch.com/2015/10/12/scraping-images-with-python-and-scrapy/

https://realpython.com/web-scraping-with-scrapy-and-mongodb/

scrape tools for airbnb:

 - js tool : https://github.com/nonlinearnarrative/scrape-airbnb

 - scrapy blog: https://www.verginer.eu/blog/web-scraping-airbnb/#setting-up-the-system

 - robust, with scrapy-splash, but doesn't quite work: https://github.com/bashedev/airbnb_scraper

 - simpler, works: https://github.com/adodd202/Airbnb_Scraping

 - another project: https://github.com/drewthayer/airbnb-data-collection/blob/master/airbnb.py

 ### using scrapy

 tutorial: https://realpython.com/web-scraping-with-scrapy-and-mongodb/

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

### scraping basics

1. check source code to see if what you want is in the page's source. Two options:
    - mac, chrome: alt+cmd+u, or view-> developer-> view source
    - save to file: requests.get().text

2. scraping w/ javascript engine
    - selenium:
        - install chromedriver (brew), export to PATH
            https://stackoverflow.com/questions/38081021/using-selenium-on-mac-chrome

        - tutorial: https://medium.com/@hoppy/how-to-test-or-scrape-javascript-rendered-websites-with-python-selenium-a-beginner-step-by-c137892216aa
