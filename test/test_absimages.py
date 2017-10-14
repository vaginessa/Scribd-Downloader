import requests
from bs4 import BeautifulSoup
import scribdl
import os


URL = 'https://www.scribd.com/document/31698781/Constitution-of-the-Mexican-Mafia-in-Texas'
images = True


def test_absimage():
    expect_absimage = True

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    absimg = soup.find('img', {'class':'absimg'}, src=True)
    print(absimg['src'])
    scribdl.save_image(absimg['src'], 'testimage.jpg')
    absimage = os.path.isfile('testimage.jpg')

    if absimage:
        os.remove('testimage.jpg')

    assert absimage == expect_absimage
