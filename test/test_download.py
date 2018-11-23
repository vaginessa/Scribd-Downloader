from scribdl.downloader import Downloader
import os

import pytest


@pytest.fixture
def cwd_to_tmpdir(tmpdir):
    os.chdir(str(tmpdir))


def test_book_download(cwd_to_tmpdir):
    book_url = "https://www.scribd.com/read/356399358/The-Boat-Runner-A-Novel"
    book_downloader = Downloader(book_url)
    md_book = book_downloader.download()
    assert os.path.getsize(md_book.input_content) in range(60000, 70000)
    md_book.to_pdf()
    assert os.path.getsize(md_book.pdf_path) in range(180000, 200000)


def test_text_document_download(cwd_to_tmpdir):
    text_doc_url = "https://www.scribd.com/document/96882378/Trademark-License-Agreement"
    text_downloader = Downloader(text_doc_url)
    md_doc = text_downloader.download(is_image_document=False)
    assert os.path.getsize(md_doc.input_content) in range(1000, 2000)
    md_doc.to_pdf()
    assert os.path.getsize(md_doc.pdf_path) in range(20000, 31000)


def test_img_document_download(cwd_to_tmpdir):
    img_doc_url = "https://www.scribd.com/doc/136711944/Signature-Scanning-and-Verification-in-Finacle"
    img_downloader = Downloader(img_doc_url)
    imgs = img_downloader.download(is_image_document=True)
    assert len(imgs.input_content) == 2
    imgs.to_pdf()
    assert os.path.getsize(imgs.pdf_path) in range(140000, 150000)
