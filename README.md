# Scribd-Downloader

- This python script allows downloading of Scribd documents.

- It does not matter if the pages are blurred or require authentication, this script will still do the job.

- There are two types of documents on Scribd:

  - Documents made up using a collection of images and
  - Actual documents where the text can be selected, copied etc.

This script takes a different approach to both of them:

- Documents consisting of a collection of images is straightforward and this script will simply download the induvidual images which can later be combined into a PDF using a suitable software. Simple.

- Actual documents where the text can be selected are hard to tackle. If you feed such a PDF in this script, only the text present in PDF will be downloaded. I do not know much about JS and since Scribd uses JS to combine text and images for each induvidual page I do not know how it works. Ideas welcome on combining images and text!

## Installation & Usage

```
git clone https://github.com/Ritiek/Scribd-Downloader
cd Scribd-Downloader
sudo pip install -r requirements.txt
python scribd.py --help
```
```
usage: scribd.py [-h] -d DOC [-i]

A Scribd-Downloader that actually works

optional arguments:
  -h, --help         show this help message and exit
  -d DOC, --doc DOC  scribd document to download
  -i, --images       download document made up of images
```

- To download text from document containing selectable text:
- example: `python scribd.py -d https://www.scribd.com/document/55949937/33-Strategies-of-War`

(Text will be saved side by side in a `.txt` file in your current working directory)

- To download document containing images; use the `--images` option:
- example: `python scribd.py -i -d http://scribd.com/doc/17142797/Case-in-Point`

(Images will be saved in a new folder created in your current working directory)

## Disclaimer

Downloading books from Scribd for free maybe prohibited. This tool is meant for research purposes only. Please support the authors by buying their titles.

## License

`The MIT License`
