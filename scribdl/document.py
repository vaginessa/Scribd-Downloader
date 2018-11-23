from bs4 import BeautifulSoup
import requests

import shutil
import os

from abc import abstractmethod
from .base import ScribdBase
from . import internals


class ScribdDocument(ScribdBase):
    """
    A base class for downloading documents off Scribd.

    Parameters
    ----------
    url : `str`
        A string containing Scribd document URL.
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_title(self):
        """
        Scrapes the title of the Scribd document.
        """
        title = self.soup.find('title').get_text()
        return internals.sanitize_title(title)

    def _extract_all_jsonp_urls(self):
        """
        Extracts all URLs ending with '.jsonp' by parsing the
        HTML code.
        """
        js_text = self.soup.find_all('script', type='text/javascript')
        jsonp_urls = []
        for opening in js_text:
            for inner_opening in opening:
                jsonp = self._extract_jsonp_url(inner_opening)
                if jsonp:
                    jsonp_urls.append(jsonp)
        return jsonp_urls

    def _extract_jsonp_url(self, inner_opening):
        """
        Extracts URLs ending with '.jsonp'. These URLs contain the
        raw document text.
        """
        portion1 = inner_opening.find('https://')

        if portion1 == -1:
            jsonp = None
        else:
            portion2 = inner_opening.find('.jsonp')
            jsonp = inner_opening[portion1:portion2+6]

        return jsonp

    @abstractmethod
    def get_content(self):
        """
        An abstract method which will fetch the actual content
        found in the '.jsonp' URLs.
        """
        pass


class ScribdTextualDocument(ScribdDocument):
    """
    A class for downloading textual documents off Scribd.
    """

    def get_content(self):
        """
        Generates the filename and processes the text extraction
        to this file.
        """
        title = self.get_title()
        jsonp_urls = self._extract_all_jsonp_urls()

        print('Extracting text to ' + title + '.md\n')
        filename = title + '.md'
        self.text_extractor(jsonp_urls, filename)
        return filename

    def get_title(self):
        """
        Scrapes the title of the Scribd document.
        """
        title = self.soup.find('title').get_text()
        return internals.sanitize_title(title)

    def text_extractor(self, jsonp_urls, filename):
        """
        Saves text from every '.jsonp' URL.
        """
        for jsonp_url in jsonp_urls:
            self.save_text(jsonp_url, filename)

    def save_text(self, jsonp, filename):
        """
        Makes a GET request to the '.jsonp' URL and saves
        the text to the passed file.
        """
        response = requests.get(jsonp).text
        page_no = response[11:12]

        response_head = (
            response).replace('window.page' + page_no + '_callback(["',
                              '').replace('\\n', '').replace('\\', '').replace(
                                  '"]);', '')
        soup_content = BeautifulSoup(response_head, 'html.parser')

        for x in soup_content.find_all('span', {'class': 'a'}):
            xtext = internals.fix_encoding(x.get_text())
            print(xtext)

            extraction = xtext + '\n\n'
            with open(filename, 'a') as feed:
                feed.write(extraction)


class ScribdImageDocument(ScribdDocument):
    """
    A class for downloading image documents off Scribd.
    """

    def get_content(self):
        """
        Processes the image extraction.
        """
        title = self.get_title()
        jsonp_urls = self._extract_all_jsonp_urls()

        # sometimes images embedded directly in html as well
        return self.image_extractor(jsonp_urls, title)

    def get_title(self):
        """
        Scrapes the title of the Scribd document.
        """
        title = self.soup.find('title').get_text()
        return internals.sanitize_title(title)

    def image_extractor(self, jsonp_urls, initial_filename):
        """
        Function for downloading images off '.jsonp' URLs to
        filenames.
        """
        downloaded_images = self._html_image_extractor(initial_filename)
        found = len(downloaded_images) > 0
        for jsonp_url in jsonp_urls[:2]:
            filename = '{}_{}.jpg'.format(initial_filename,
                                          len(downloaded_images) + 1)
            self.save_image(jsonp_url, filename, found)
            downloaded_images.append(filename)
        return downloaded_images

    def _html_image_extractor(self, initial_filename):
        """
        Extracts images that are directly embedded in the original
        HTML page.
        """
        downloaded_images = []
        absimg = self.soup.find_all('img', {'class':'absimg'}, src=True)
        for img in absimg:
            filename = '{}_{}.jpg'.format(initial_filename,
                                          len(downloaded_images) + 1)
            self.save_image(img['src'], filename, found=False)
            downloaded_images.append(filename)
        return downloaded_images

    def convert_to_image_url(self, url, found):
        """
        Gets the image URL corresponding to the '.jsonp' URL.
        """
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
        """
        Skips downloading if the image is already downloaded,
        otherwise downloads it locally.
        """
        print("Downloading " + imagename)
        already_present = os.listdir('.')
        if imagename in already_present:
            return

        url = self.convert_to_image_url(jsonp_url, found)
        response = requests.get(url, stream=True)
        with open(imagename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
