import requests
import json

from .base import ScribdBase


class ScribdBook(ScribdBase):
    """
    A class for downloading books off Scribd.

    Parameters
    ----------
    url : `str`
        A string containing Scribd book URL.
    """

    def __init__(self, url):
        self.url = url

    def _extract_text(self, content):
        """
        Extracts text given a block of raw html.
        """
        words = []
        for word in content["words"]:
            if word.get("break_map", None):
                words.append(word["break_map"]["text"])
            elif word.get("text", None):
                words.append(word["text"])
            else:
                words += self._extract_text(word)
        return words

    def get_content(self):
        """
        Processing text and image extraction.
        """
        book_id = str(self.get_id())
        token = self._get_token(book_id)

        filename = book_id + ".md"
        chapter = 1

        while True:
            response = self.fetch_response(book_id, chapter, token)

            if response.status_code == 403:
                token = self._get_token(book_id)
                response = self.fetch_response(book_id, chapter, token)

                if response.status_code == 403:
                    print("No more content being exposed by Scribd!")
                    break

            json_response = json.loads(response.text)
            self._extract_text_blocks(
                json_response, book_id, chapter, token, filename
            )

            chapter += 1

        return filename

    def fetch_response(self, book_id, chapter, token):
        url = self._format_content_url(book_id, chapter, token)
        response = requests.get(url)
        return response

    def _extract_text_blocks(self, response_dict, book_id, chapter, token, filename):
        """
        Extracts small blocks of raw book text and image
        URLs and writes them to a file.
        """
        for block in response_dict["blocks"]:
            if block["type"] == "text":
                string_text = " ".join(self._extract_text(block)) + "\n\n"
            elif block["type"] == "image":
                image_url = self._format_image_url(
                    book_id, chapter, block["src"], token
                )
                imagename = block["src"].replace("images/", "")
                string_text = "![{}]({})\n\n".format(imagename, image_url)

            if block["type"] in ("text", "image"):
                print(string_text)
                self.save_text(string_text, filename)

    def _format_content_url(self, book_id, chapter, token):
        """
        Generates a string which points to a URL containing
        the raw book text.
        """
        unformatted_url = (
            "https://www.scribd.com/scepub/{}/chapters/{}/" "contents.json?token={}"
        )
        return unformatted_url.format(book_id, chapter, token)

    def _format_image_url(self, book_id, chapter, image, token):
        """
        Generates a string which points to an image URL.
        """
        unformatted_url = "https://www.scribd.com/scepub/{}/chapters/{}/" "{}?token={}"
        return unformatted_url.format(book_id, chapter, image, token)

    def get_id(self):
        """
        Extracts the book ID.
        """
        splits = self.url.split("/")
        for split in splits:
            try:
                book_id = int(split)
            except ValueError:
                continue
        return book_id

    def _get_token(self, book_id):
        """
        Fetches a uniquely generated token for the current
        session.
        """
        token_url = "https://www.scribd.com/read2/{}/access_token".format(book_id)
        token = requests.post(token_url)
        return json.loads(token.text)["response"]

    def save_text(self, string_text, filename):
        """
        Writes text to the passed file.
        """
        with open(filename, "a") as f:
            f.write(string_text)
