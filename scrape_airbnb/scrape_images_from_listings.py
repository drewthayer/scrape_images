import urllib.request
from bs4 import BeautifulSoup
import urllib3
import os
import json
import sys


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
    # cmd line args
    city = sys.argv[1]      # e.g. 'Denver'
    state = sys.argv[2]     # e.g. 'CO'

    # set directories
    cwd = os.getcwd()
    img_dir = cwd + '/images/' + city + '/'
    listing_dir = cwd + '/listings/'

    # load listings json file
    fname = 'airbnb_{}_{}.json'.format(city, state)
    with open(listing_dir + fname, 'r') as f:
        listings = json.load(f)

    # scrape images from listings
    for id in listings.keys():
        data = listings[id]
        url = data['url']
        # extract image links
        links = extract_image_urls(url)
        # save images with sequential names
        savename = '{}_{}_{}'.format(city, state, id)
        save_images_sequential(links, savename, img_dir)
