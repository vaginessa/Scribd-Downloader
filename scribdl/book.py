import requests
import json
import os
import shutil

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
        self.book_id = str(self.get_id())

    def _extract_text(self, content, chapter, token):
        """
        Extracts text given a block of raw html.
        """
        words = []
        for word in content["words"]:
            if word.get("break_map", None):
                words.append(word["break_map"]["text"])
            elif word.get("text", None):
                words.append(word["text"])
            elif word.get("type", None) == "image":
                image_url = self._format_image_url(chapter, word["src"], token)
                string_text = self._process_image_text(word, image_url)
                words.append(string_text)
            else:
                words += self._extract_text(word, chapter, token)
        return words

    def get_content(self):
        """
        Processing text and image extraction.
        """
        token = self._get_token()

        filename = self.book_id + ".md"
        chapter = 1

        while True:
            response = self.fetch_response(chapter, token)

            if response.status_code == 403:
                token = self._get_token()
                response = self.fetch_response(chapter, token)

                if response.status_code == 403:
                    print("No more content being exposed by Scribd!")
                    break

            try:
                json_response = json.loads(response.text)
            except ValueError:
                print("Completed downloading book!")
                break

            self._extract_text_blocks(json_response, chapter, token, filename)

            chapter += 1

        return filename

    def fetch_response(self, chapter, token):
        url = self._format_content_url(chapter, token)
        response = requests.get(url)
        return response

    def _extract_text_blocks(self, response_dict, chapter, token, filename):
        """
        Extracts small blocks of raw book text and image
        URLs and writes them to a file.
        """
        for block in response_dict["blocks"]:
            if block["type"] == "text":
                string_text = (
                    " ".join(self._extract_text(block, chapter, token)) + "\n\n"
                )
            elif block["type"] == "image":
                image_url = self._format_image_url(chapter, block["src"], token)
                string_text = self._process_image_text(block, image_url)

            if block["type"] in ("text", "image"):
                print(string_text)
                self.save_text(string_text, filename)

    def _process_image_text(self, block, image_url):
        image_name = block["src"].replace("images/", "")
        image_path = os.path.join(self.book_id, image_name)
        self._download_image(image_url, image_path)
        string_text = "![{}]({})\n\n".format(image_name, image_path)
        return string_text

    def _download_image(self, url, path):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass
        response = requests.get(url, stream=True)
        with open(path, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)

    def _extract_image_path_from_url(self, url):
        image_name = url.split("/")[-1].split("?token=")[0]
        return os.path.join(self.book_id, image_name)

    def _format_content_url(self, chapter, token):
        """
        Generates a string which points to a URL containing
        the raw book text.
        """
        unformatted_url = (
            "https://www.scribd.com/scepub/{}/chapters/{}/" "contents.json?token={}"
        )
        return unformatted_url.format(self.book_id, chapter, token)

    def _format_image_url(self, chapter, image, token):
        """
        Generates a string which points to an image URL.
        """
        unformatted_url = "https://www.scribd.com/scepub/{}/chapters/{}/" "{}?token={}"
        return unformatted_url.format(self.book_id, chapter, image, token)

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

    def _get_token(self):
        """
        Fetches a uniquely generated token for the current
        session.
        """
        headers = {
            "X-CSRF-Token": "jfHAQ/LjqJAexQtAkCgWi0hif/sWHi5pXVAHCNsC3GkZocGcHcfETUhZ/Wd+YyY0tEH/zV/hRCOZhyq7ZewiMQ=="
        }
        cookies = {
            "_scribd_session": "eyJzZXNzaW9uX2lkIjoiNTg3N2VjOTAwMGNmOTM5M2IwMGEwY2ExZmI2YTRiOTQiLCJfY3NyZl90b2tlbiI6ImxGQUIzKzhrYk4xV25QWW43a3N3di93amdEWkovMnBLeE5jdHM3N3UvbGc9IiwiciI6IjE1NDM2Mjk1ODAiLCJ3b3JkX2lkIjoyNjMzNjM2MzIsInAiOjE1NDI5MzQ4NDMsImxhc3RfcmVhdXRoIjoxNTQzNjI5NTgwfQ%3D%3D--4f34750fb7295b3b6f26754547c2e1e568da3e86",
            "_scribd_expire": "1543629580",
        }
        data = "data"

        token_url = "https://www.scribd.com/read2/{}/access_token".format(self.book_id)
        token = requests.post(token_url, headers=headers, cookies=cookies, data=data)
        return json.loads(token.text)["response"]

    def save_text(self, string_text, filename):
        """
        Writes text to the passed file.
        """
        with open(filename, "a") as f:
            f.write(string_text)
