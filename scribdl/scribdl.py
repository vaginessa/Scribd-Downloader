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
from abc import ABC, abstractmethod


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

class ScribdBase(ABC):
    @abstractmethod
    def get_content(self):
        pass

class ScribdDocument(ScribdBase):
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_title(self):
        title = self.soup.find('title').get_text()
        return sanitize_title(title)

    def _extract_all_jsonp_urls(self):
        js_text = self.soup.find_all('script', type='text/javascript')
        jsonp_urls = []
        for opening in js_text:
            for inner_opening in opening:
                jsonp = self._extract_jsonp_url(inner_opening)
                if jsonp:
                    jsonp_urls.append(jsonp)
        return jsonp_urls

    def _extract_jsonp_url(self, inner_opening):
        portion1 = inner_opening.find('https://')

        if portion1 == -1:
            jsonp = None
        else:
            portion2 = inner_opening.find('.jsonp')
            jsonp = inner_opening[portion1:portion2+6]

        return jsonp

    @abstractmethod
    def get_content(self):
        pass


class ScribdTextualDocument(ScribdDocument):
    def get_content(self):
        title = self.get_title()
        jsonp_urls = self._extract_all_jsonp_urls()

        print('Extracting text to ' + title + '.md\n')
        filename = title + '.md'
        self.text_extractor(jsonp_urls, filename)
        return filename

    def get_title(self):
        title = self.soup.find('title').get_text()
        return sanitize_title(title)

    def text_extractor(self, jsonp_urls, filename):
        for jsonp_url in jsonp_urls:
            self.save_text(jsonp_url, filename)

    def save_text(self, jsonp, filename):
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


class ScribdImageDocument(ScribdDocument):
    def get_content(self):
        title = self.get_title()
        jsonp_urls = self._extract_all_jsonp_urls()

        # sometimes images embedded directly in html as well
        return self.image_extractor(jsonp_urls, title)

    def get_title(self):
        title = self.soup.find('title').get_text()
        return sanitize_title(title)

    def image_extractor(self, jsonp_urls, initial_filename):
        downloaded_images = self._html_image_extractor(initial_filename)
        found = len(downloaded_images) > 0
        for jsonp_url in jsonp_urls:
            filename = '{}_{}.jpg'.format(initial_filename,
                                          len(downloaded_images) + 1)
            self.save_image(jsonp_url, filename, found)
            downloaded_images.append(filename)
        return downloaded_images

    def _html_image_extractor(self, initial_filename):
        downloaded_images = []
        absimg = self.soup.find_all('img', {'class':'absimg'}, src=True)
        for img in absimg:
            filename = '{}_{}.jpg'.format(initial_filename,
                                          len(downloaded_images) + 1)
            self.save_image(img['src'], filename, found=False)
            downloaded_images.append(filename)
        return downloaded_images

    def convert_to_image_url(self, url, found):
        if url.endswith('.jsonp'):
            replacement = url.replace('/pages/', '/images/')
            if found:
                replacement = replacement.replace('.jsonp', '/000.jpg')
            else:
                replacement = replacement.replace('.jsonp', '.jpg')
        else:
            replacement = url

        return replacement

    def save_image(self, jsonp_url, imagename, found=False):
        print("Downloading " + imagename)
        already_present = os.listdir('.')
        if imagename in already_present:
            return

        url = self.convert_to_image_url(jsonp_url, found)
        response = requests.get(url, stream=True)
        with open(imagename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)


class ScribdBook(ScribdBase):
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

    def get_content(self):
        book_id = str(self.get_id())
        token = self._get_token(book_id)

        filename = book_id + '.md'
        chapter = 1

        while True:
            url = self._format_content_url(book_id, chapter, token)
            response = requests.get(url)

            try:
                json_response = json.loads(response.text)
                self._extract_text_blocks(json_response,
                                          book_id,
                                          chapter,
                                          token,
                                          filename)
                chapter += 1

            except ValueError:
                print('No more content being exposed by Scribd!')
                break

        return filename

    def _extract_text_blocks(self, response_dict, book_id, chapter, token, filename):
        for block in response_dict['blocks']:
            if block['type'] == 'text':
                string_text = ' '.join(self._extract_text(block)) + '\n\n'
            elif block['type'] == 'image':
                image_url = self._format_image_url(book_id, chapter, block['src'], token)
                imagename = block['src'].replace('images/', '')
                string_text = '![{}]({})\n\n'.format(imagename, image_url)

            if block['type'] in ('text', 'image'):
                print(string_text)
                self.save_text(string_text, filename)

    def _format_content_url(self, book_id, chapter, token):
        unformatted_url = ('https://www.scribd.com/scepub/{}/chapters/{}/'
                          'contents.json?token={}')
        return unformatted_url.format(book_id, chapter, token)

    def _format_image_url(self, book_id, chapter, image, token):
        unformatted_url = ('https://www.scribd.com/scepub/{}/chapters/{}/'
                          '{}?token={}')
        return unformatted_url.format(book_id, chapter, image, token)

    def get_id(self):
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

    def save_text(self, string_text, filename):
            with open(filename, 'a') as f:
                f.write(string_text)


class ConvertToPDF:
    def __init__(self, input_content, output_path):
        self.input_content = input_content
        self.pdf_path = output_path

    def to_pdf(self):
        if isinstance(self.input_content, list):
            self._images_to_pdf()
        else:
            self._markdown_to_pdf()

    def _markdown_to_pdf(self):
        with open(self.input_content, 'rb') as f:
            string_text = f.read()
        md2pdf(self.pdf_path, md_content=string_text)

    def _images_to_pdf(self):
        with open(self.pdf_path, 'wb') as f:
            open_images = [open(img, 'rb') for img in self.input_content]
            pdf_images = img2pdf.convert(open_images)
            f.write(pdf_images)


class Downloader:
    def __init__(self, url):
        self.url = url
        self._is_book = self.is_book()

    def download(self, is_image_document=None):
        if self._is_book:
            content = self._download_book()
        else:
            if is_image_document is None:
                raise TypeError("The input URL points to a document. You must specify "
                                "whether it is an image document or a textual document "
                                "in the `image_document` parameter.")
            content = self._download_document(is_image_document)

        return content

    def _download_book(self):
        book = ScribdBook(self.url)
        md_path = book.get_content()
        pdf_path = '{}.pdf'.format(book.get_id())
        return ConvertToPDF(md_path, pdf_path)

    def _download_document(self, image_document):
        if image_document:
            document = ScribdImageDocument(self.url)
        else:
            document = ScribdTextualDocument(self.url)

        content_path = document.get_content()
        pdf_path = '{}.pdf'.format(document.get_title())
        return ConvertToPDF(content_path, pdf_path)

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
    downloaded_content = scribd_link.download(is_image_document=images)
    if pdf:
        print("\nConverting to {}..".format(downloaded_content.pdf_path))
        downloaded_content.to_pdf()


if __name__ == '__main__':
    _command_line()
