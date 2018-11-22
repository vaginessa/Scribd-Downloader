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
        'url',
        metavar='URL',
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


# class ScribdImageDocument(ScribdDocument):
# class ScribdTextualDocument(ScribdDocument):

class ScribdDocument:
    def __init__(self, url, image_document):
        self.url = url
        self.image_document = image_document
        self.images_list = []

    def get_document(self):
        response = requests.get(self.url).text
        soup = BeautifulSoup(response, 'html.parser')

        title = soup.find('title').get_text()
        title = sanitize_title(title)
        train = 1
        print(title + '\n')

        if self.image_document:
            # sometimes images embedded directly in html as well
            absimg = soup.find_all('img', {'class':'absimg'}, src=True)
            for img in absimg:
                #train = self._save_content(img['src'], True, train, title)
                filename = '{}_{}.jpg'.format(title, train)
                self._save_image(img['src'], filename, found=False)
                train += 1
        else:
            print('Extracting text to ' + title + '.md\n')

        found = train > 1
        js_text = soup.find_all('script', type='text/javascript')

        for opening in js_text:

            for inner_opening in opening:
                portion1 = inner_opening.find('https://')

                if not portion1 == -1:
                    portion2 = inner_opening.find('.jsonp')
                    jsonp = inner_opening[portion1:portion2+6]

                    #train = self._save_content(jsonp, train, title, found)
                    if jsonp:
                        if self.image_document:
                            filename = '{}_{}.jpg'.format(title, train)
                            self._save_image(jsonp, filename, found)
                            train += 1
                        else:
                            filename = title + '.md'
                            self._save_text(jsonp, filename)


    def _save_image(self, content, imagename, found=False):
        print("Downloading " + imagename)
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
        print("Appending text to " + filename)
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

            extraction = xtext + '\n\n'
            with open(filename, 'a') as feed:
                feed.write(extraction)

    # detect image and text
    def _save_content(self, content, train, title, found=False):
        if not content == '':
            if self.image_document:
                imagename = title + '_' + str(train) + '.jpg'
                print('Downloading image to ' + imagename)
                self._save_image(content, imagename, found)
            else:
                self._save_text(content, (title + '.txt'))
            train += 1

        return train


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
        book_id = str(self._get_book_id())
        token = self._get_token(book_id)

        filename = book_id + '.md'
        chapter = 1

        while True:
            url = self._format_content_url(book_id, chapter, token)
            response = requests.get(url)

            try:
                json_response = json.loads(response.text)
                for block in json_response['blocks']:
                    if block['type'] == 'text':
                        string_text = ' '.join(self._extract_text(block)) + '\n\n'
                    elif block['type'] == 'image':
                        image_url = self._format_image_url(book_id, chapter, block['src'], token)
                        imagename = block['src'].replace('images/', '')
                        string_text = '![{}]({})\n\n'.format(imagename, image_url)

                    if block['type'] in ('text', 'image'):
                        print(string_text)
                        self._save_text(string_text, filename)

                chapter += 1

            except ValueError:
                print('No more content being exposed by Scribd!')
                break

        return filename

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

    def _save_text(self, string_text, filename):
            with open(filename, 'a') as f:
                f.write(string_text)


class ConvertToPDF:
    def __init__(self, input_content, output_path):
        self.input_content = input_content
        self.output_path = output_path

    def convert_to_pdf(self):
        if isinstance(self.input_content, list):
            self._images_to_pdf()
        else:
            self._markdown_to_pdf()

    def _markdown_to_pdf(self):
        with open(self.input_content, 'rb') as f:
            string_text = f.read()
        md2pdf(self.output_path, md_content=string_text)

    def _images_to_pdf(self):
        with open(self.output_path, 'wb') as f:
            open_images = [open(img, 'rb') for img in self.input_content]
            pdf_images = img2pdf.convert(open_images)
            f.write(pdf_images)


class Downloader:
    def __init__(self, url):
        self.url = url
        self._is_book = self.is_book()

    def download(self, is_image_document=None):
        if self._is_book:
            book_path = self._download_book()
        else:
            if is_image_document is None:
                raise TypeError("The input URL points to a document. You must specify "
                                "whether it is an image document or a textual document "
                                "in the `image_document` parameter.")
            document_path = self._download_document(is_image_document)

    def _download_book(self):
        book = ScribdBook(self.url)
        downloaded_book = book.get_book()

    def _download_document(self, image_document):
        document = ScribdDocument(self.url, image_document)
        downloaded_document = document.get_document()

    def is_book(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content_class = soup.find('body')['class']
        matches_with_book = content_class[0] == "autogen_class_views_layouts_book_web"
        return matches_with_book


def _command_line():
    args = get_arguments()
    url = args.url
    pdf = args.pdf
    images = args.images
    scribd_link = Downloader(url)
    scribd_link.download(is_image_document=images)


if __name__ == '__main__':
    _command_line()
