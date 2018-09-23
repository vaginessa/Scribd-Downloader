import requests
from bs4 import BeautifulSoup
from scribdl import scribdl
import os


URL = 'https://www.scribd.com/document/55949937/33-Strategies-of-War'
images = False


def test_jsonp():
    expect_jsonp = 'https://html2-f.scribdassets.com/8u7q15n1q8z07to/pages/1-a9de44b065.jsonp'

    response = requests.get(url=URL).text
    soup = BeautifulSoup(response, 'html.parser')

    js_text = soup.find_all('script', type='text/javascript')
    inner_opening = js_text[16].get_text()

    portion1 = inner_opening.find('https://')
    portion2 = inner_opening.find('.jsonp')
    global jsonp
    jsonp = inner_opening[portion1:portion2+6]

    assert jsonp == expect_jsonp


def test_text():
    with open('test/expect_text.txt', 'r') as textin:
        expect_text = textin.read()

    scribdl.save_text(jsonp, 'text.txt')

    with open('text.txt', 'r') as textin:
        text = textin.read()

    if os.path.isfile('text.txt'):
        os.remove('text.txt')

    assert text == expect_text
