import urllib.request
from bs4 import BeautifulSoup
import urllib3
import os


def make_soup(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)
    return soup


def extract_image_urls(url):
    # parse html with BeautifulSoup
    soup = make_soup(url)
    # extract all 'img' handles from soup
    images = [img for img in soup.findAll('img')]
    print (str(len(images)) + " images found.")

    #compile unicode list of image links
    image_links = [each.get('src') for each in images]

    # retreive images from links
    links = []
    for link in image_links:
        filename = link.split('/')[-1]
        if 'profile' not in filename and 'user' not in filename:
            print(filename)
            links.append(link)
    return links


def save_images_sequential(links, fid, savepath):
    c = 1
    for link in links:
        fname = '{}_{}.png'.format(fid, c)
        urllib.request.urlretrieve(link, savepath + fname)
        c += 1
    print('{} images written'.format(c-1))


if __name__=='__main__':
    cwd = os.getcwd()
    savepath = cwd + '/images/'
    #url = 'https://www.airbnb.com/rooms/5185375?location=Denver%2C%20CO%2C%20United%20States&adults=2&guests=1&s=aWMV5CJc'
    #url = 'https://www.airbnb.com/rooms/521072?location=Denver%2C%20CO%2C%20United%20States&s=u6RjtbVm'
    url = 'https://www.airbnb.com/rooms/13172589?location=Denver%2C%20CO%2C%20United%20States&s=u6RjtbVm'

    # extract image links
    links = extract_image_urls(url)

    # save images with sequential names
    fid = '00003' # loop this for multiple calls
    save_images_sequential(links, fid, savepath)
