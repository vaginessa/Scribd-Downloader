from bs4 import BeautifulSoup
import requests

from .document import ScribdTextualDocument
from .document import ScribdImageDocument
from .book import ScribdBook

from .pdf_converter import ConvertToPDF


class Downloader:
    """
    A helper class for downloading books and documents off Scribd.

    Parameters
    ----------
    url : `str`
        A string containing path to a Scribd URL
    """

    def __init__(self, url):
        self.url = url
        self._is_book = self.is_book()

    def download(self, is_image_document=None):
        """
        Downloads books and documents from Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        if self._is_book:
            content = self._download_book()
        else:
            if is_image_document is None:
                raise TypeError(
                    "The input URL points to a document. You must specify "
                    "whether it is an image document or a textual document "
                    "in the `image_document` parameter."
                )
            content = self._download_document(is_image_document)

        return content

    def _download_book(self):
        """
        Downloads books off Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        book = ScribdBook(self.url)
        md_path = book.get_content()
        pdf_path = "{}.pdf".format(book.get_id())
        return ConvertToPDF(md_path, pdf_path)

    def _download_document(self, image_document):
        """
        Downloads textual and image documents off Scribd.
        Returns an object of `ConvertToPDF` class.
        """
        if image_document:
            document = ScribdImageDocument(self.url)
        else:
            document = ScribdTextualDocument(self.url)

        content_path = document.get_content()
        pdf_path = "{}.pdf".format(document.get_title())
        return ConvertToPDF(content_path, pdf_path)

    def is_book(self):
        """
        Checks whether the passed URL points to a Scribd book
        or a Scribd document
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        content_class = soup.find("body")["class"]
        matches_with_book = content_class[0] == "autogen_class_views_layouts_book_web"
        return matches_with_book
