from scribdl.downloader import Downloader
import os

import pytest


@pytest.fixture
def cwd_to_tmpdir(tmpdir):
    os.chdir(tmpdir)


def test_book_download(cwd_to_tmpdir):
    book_url = "https://www.scribd.com/read/356399358/The-Boat-Runner-A-Novel"
    book_downloader = Downloader(book_url)
    md_book = book_downloader.download()
    assert os.path.getsize(md_book.input_content) == 64733
    md_book.to_pdf()
    assert os.path.getsize(md_book.pdf_path) == 185841


def test_text_document_download(cwd_to_tmpdir):
    text_doc_url = "https://www.scribd.com/document/96882378/Trademark-License-Agreement"
    text_downloader = Downloader(text_doc_url)
    md_doc = text_downloader.download(is_image_document=False)
    assert os.path.getsize(md_doc.input_content) == 1431
    md_doc.to_pdf()
    assert os.path.getsize(md_doc.pdf_path) == 27874


def test_img_document_download(cwd_to_tmpdir):
    img_doc_url = "https://www.scribd.com/doc/136711944/Signature-Scanning-and-Verification-in-Finacle"
    img_downloader = Downloader(img_doc_url)
    imgs = img_downloader.download(is_image_document=True)
    assert len(imgs.input_content) == 2
    imgs.to_pdf()
    assert os.path.getsize(imgs.pdf_path) == 147980
