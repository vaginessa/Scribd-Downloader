#!/usr/bin/env python

from bs4 import BeautifulSoup
import img2pdf
from md2pdf.core import md2pdf
import os
import requests
import shutil
import sys
import json
import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Download documents/text from scribd.com')

    parser.add_argument(
        'content',
        metavar='CONTENT',
        type=str,
        help='scribd url to download')
    parser.add_argument(
        '-i',
        '--images',
        help="download url made up of images",
        action='store_true',
        default=False)
    parser.add_argument(
        '-p',
        '--pdf',
        help='convert images to pdf (*Nix: imagemagick)',
        action='store_true',
        default=False)

    return parser.parse_args()


def is_book(url):
    return '/book/' in url or '/read/' in url


# fix encoding issues in python2
def fix_encoding(query):
    if sys.version_info > (3, 0):
        return query
    else:
        return query.encode('utf-8')


def sanitize_title(title):
    '''
    Remove forbidden characters from title that will prevent OS from creating directory. (For Windows at least.)
    Also change ' ' to '_' to preserve previous behavior.
    '''
    forbidden_chars = " *\"/\<>:|(),"
    replace_char = "_"

    for ch in forbidden_chars:
        title = title.replace(ch, replace_char)

    return title


class ScribdDocument:
    def __init__(self, url, images, pdf):
        self.url = url
        self.images = images
        self.images_list = []
        self.pdf = pdf

    def get_document(self):
        response = requests.get(self.url).text
        soup = BeautifulSoup(response, 'html.parser')

        title = soup.find('title').get_text()
        title = sanitize_title(title)
        train = 1
        print(title + '\n')

        if self.images:
            # sometimes images embedded directly in html as well
            absimg = soup.find_all('img', {'class':'absimg'}, src=True)
            for img in absimg:
                train = self._save_content(img['src'], True, train, title)
        else:
            print('Extracting text to ' + title + '.txt\n')

        found = train > 1
        js_text = soup.find_all('script', type='text/javascript')

        for opening in js_text:

            for inner_opening in opening:
                portion1 = inner_opening.find('https://')

                if not portion1 == -1:
                    portion2 = inner_opening.find('.jsonp')
                    jsonp = inner_opening[portion1:portion2+6]

                    train = self._save_content(jsonp, train, title, found)

        if self.pdf:
            self._convert_to_pdf(title)

    def _save_image(self, content, imagename, found=False):
        already_present = os.listdir('.')
        if imagename in already_present:
            return

        if content.endswith('.jsonp'):
            replacement = content.replace('/pages/', '/images/')
            if found:
                replacement = replacement.replace('.jsonp', '/000.jpg')
            else:
                replacement = replacement.replace('.jsonp', '.jpg')
        else:
            replacement = content

        response = requests.get(replacement, stream=True)
        with open(imagename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            self.images_list.append(imagename)

    def _save_text(self, jsonp, filename):
        response = requests.get(jsonp).text
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
    def _save_content(self, content, train, title, found=False):
        if not content == '':
            if self.images:
                imagename = title + '_' + str(train) + '.jpg'
                print('Downloading image to ' + imagename)
                self._save_image(content, imagename, found)
            else:
                self._save_text(content, (title + '.txt'))
            train += 1

        return train

    def _convert_to_pdf(title):
        if self.images_list:
            try:
                with open(title.strip('_') + '.pdf', 'wb') as f:
                    f.write(img2pdf.convert([open(img, 'rb') for img in self.images_list]))
                print('PDF file generated.')
            except Exception as e:
                print('PDF conversion failed: ' + str(e))


class ScribdBook:
    def __init__(self, url):
        self.url = url

    def _extract_text(self, content):
        words = []
        for word in content['words']:
            if word.get('break_map', None):
                words.append(word['break_map']['text'])
            elif word.get('text', None):
                words.append(word['text'])
            else:
                words += self._extract_text(word)
        return words

    def get_book(self):
        book_id = self._get_book_id()
        token = self._get_token(book_id)

        chapter = 1
        string_text = ''

        while True:
            url = self._format_content_url(book_id, chapter, token)
            response = requests.get(url)

            try:
                json_response = json.loads(response.text)
                for block in json_response['blocks']:
                    if block['type'] == 'text':
                        string_text += ' '.join(self._extract_text(block)) + '\n\n'
                        print(string_text)
                    elif block['type'] == 'image':
                        image_url = self._format_image_url(book_id, chapter, block['src'], token)
                        imagename = block['src'].replace('images/', '')
                        string_text += '![{}]({})\n\n'.format(imagename, image_url)

                chapter += 1

            except json.decoder.JSONDecodeError:
                print('No more content being exposed by Scribd!')
                pdf_out = '{}.pdf'.format(book_id)
                print('Generating PDF file: {}'.format(pdf_out))
                md2pdf(pdf_out, md_content=string_text)
                break

    def _format_content_url(self, book_id, chapter, token):
        unformatted_url = ('https://www.scribd.com/scepub/{}/chapters/{}/'
                          'contents.json?token={}')
        return unformatted_url.format(book_id, chapter, token)

    def _format_image_url(self, book_id, chapter, image, token):
        unformatted_url = ('https://www.scribd.com/scepub/{}/chapters/{}/'
                          '{}?token={}')
        return unformatted_url.format(book_id, chapter, image, token)

    def _get_book_id(self):
        splits = self.url.split('/')
        for split in splits:
            try:
                book_id = int(split)
            except ValueError:
                continue
        return book_id

    def _get_token(self, book_id):
        token_url = 'https://www.scribd.com/read2/{}/access_token'.format(book_id)
        token = requests.post(token_url)
        return json.loads(token.text)['response']


def command_line():
    args = get_arguments()
    url = args.content
    if is_book(url):
        book = ScribdBook(url)
        book.get_book()
    else:
        images = args.images
        pdf = args.pdf
        document = ScribdDocument(url, images, pdf)
        document.get_document()


if __name__ == '__main__':

    command_line()
