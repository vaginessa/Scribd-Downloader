#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import shutil
import sys
import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Download documents/text from scribd.com')

    parser.add_argument(
        'doc',
        metavar='DOC',
        type=str,
        help='scribd document to download')
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


def save_image(jsonp, imagename):
    replacement = jsonp.replace('/pages/', '/images/').replace('jsonp', 'jpg')
    response = requests.get(replacement, stream=True)

    with open(imagename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def save_text(jsonp, filename):
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
        with open(filename, 'a') as feed:
            feed.write(extraction)


# detect image and text
def save_content(jsonp, images, train, title):
    if not jsonp == '':
        if images:
            imagename = title + '_' + str(train) + '.jpg'
            print('Downloading image to ' + imagename)
            save_image(jsonp, imagename)
        else:
            save_text(jsonp, (title + '.txt'))
        train += 1

    return train


def sanitize_title(title):
    '''Remove forbidden characters from title that will prevent OS from creating directory. (For Windows at least.)

    Also change ' ' to '_' to preserve previous behavior.'''

    forbidden_chars = " *\"/\<>:|"
    replace_char = "_"

    for ch in forbidden_chars:
        title = title.replace(ch, replace_char)

    return title


# the main function
def get_scribd_document(url, images):
    response = requests.get(url=url).text
    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find('title').get_text()#.replace(' ', '_')
    title = sanitize_title(title) # a bit more thorough

    if not images:
        print('Extracting text to ' + title + '.txt\n')

    print(title + '\n')

    js_text = soup.find_all('script', type='text/javascript')
    train = 1

    for opening in js_text:

        for inner_opening in opening:
            portion1 = inner_opening.find('https://')

            if not portion1 == -1:
                portion2 = inner_opening.find('.jsonp')
                jsonp = inner_opening[portion1:portion2+6]

                train = save_content(jsonp, images, train, title)


def command_line():
    args = get_arguments()
    url = args.doc
    images = args.images
    get_scribd_document(url, images)


if __name__ == '__main__':

    command_line()
