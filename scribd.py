#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import sys
import shutil
import os
import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        description='A Scribd-Downloader that actually works')

    parser.add_argument(
        '-d', '--doc', help='scribd document to download', required=True)
    parser.add_argument(
        '-i',
        '--images',
        help="download document made up of images",
        action='store_true',
        default=False)

    return parser.parse_args()


# fix encoding issues in python2
def fix_encoding(query):
    if sys.version_info > (3, 0):
        return query
    else:
        return query.encode('utf-8')


def save_image(jsonp, train, title):
    replacement = jsonp.replace('/pages/', '/images/').replace('jsonp', 'jpg')
    response = requests.get(replacement, stream=True)

    with open(title + '/pic' + str(train) + '.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def save_text(jsonp, title):
    response = requests.get(url=jsonp).text
    page_no = response[11:12]

    response_head = (
        response).replace('window.page' + page_no + '_callback(["',
                          '').replace('\\n', '').replace('\\', '').replace(
                              '"]);', '')
    soup_content = BeautifulSoup(response_head, 'html.parser')

    for x in soup_content.find_all('span', {'class': 'a'}):
        xtext = fix_encoding(x.get_text())
        print(xtext)

        extraction = xtext + '\n'
        with open((title + '.txt'), 'a') as feed:
            feed.write(extraction)


# detect image and text
def save_content(jsonp, images, train, title):
    if jsonp == '':
        return train
    else:
        if images:
            print('Downloading page ' + str(train))
            save_image(jsonp, train, title)
        else:
            save_text(jsonp, title)

        return train + 1


def clean_existing(title):
    if images:
        if not os.path.exists(title):
            os.makedirs(title)
    else:
        if os.path.exists(title + '.txt'):
            os.remove(title + '.txt')


# the main function
def get_scribd_document(url, images):
    response = requests.get(url=url).text
    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find('title').get_text().replace(' ', '_')
    print(soup.find('title').get_text() + '\n')

    clean_existing(title)

    js_text = soup.find_all('script', type='text/javascript')
    train = 1
    for opening in js_text:
        for inner_opening in opening:
            portion1 = inner_opening.find('https://')

            if not portion1 == -1:
                portion2 = inner_opening.find('.jsonp')
                jsonp = inner_opening[portion1:portion2 + 6]

                train = save_content(jsonp, images, train, title)


if __name__ == '__main__':

    os.chdir(sys.path[0])

    args = get_arguments()
    url = args.doc
    images = args.images

    get_scribd_document(url, images)
