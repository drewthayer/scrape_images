import urllib.request
from bs4 import BeautifulSoup
import urllib3
import os


def make_soup(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)
    return soup

def extract_images(url, savepath):
    # parse html with BeautifulSoup
    soup = make_soup(url)
    # extract all 'img' handles from soup
    images = [img for img in soup.findAll('img')]
    print (str(len(images)) + " images found.")

    #compile unicode list of image links
    image_links = [each.get('src') for each in images]

    # retreive images from links
    for link in image_links:
        filename = link.split('/')[-1]
        if 'profile' not in filename and 'user' not in filename:
            print(filename)
            urllib.request.urlretrieve(link, savepath + filename)

if __name__=='__main__':
    cwd = os.getcwd()
    savepath = cwd + '/images/'
    url = 'https://www.airbnb.com/rooms/5185375?location=Denver%2C%20CO%2C%20United%20States&adults=2&guests=1&s=aWMV5CJc'


    # extract images
    extract_images(url, savepath)
