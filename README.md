# Scribd-Downloader

## Introduction:

◘ This python script allows downloading scribd documents.

◘ It does not matter if the pages are blurred and require authentication, this script will still do the job.

◘ There are two types of PDF's on Scribd:

- PDF's made up using a collection of images and
- Actual PDF's where the text can be selected, copied etc.

This script takes a different approach to each of them:

◘ PDF's consisting of a collection of images is straightforward and this script will simply download the induvidual images which can later be combined into a PDF using a suitable software. Simple.

◘ Actual PDF's where the text can be selected are hard to tackle. If you feed such a PDF in this script, only the text present in PDF will be downloaded. I do not know much about JS and since Scribd uses javascript to combine text and images for each induvidual page (for PDF's like these) I do not know how it works.

## Installation & Usage:

```
git clone https://github.com/Ritiek/Scribd-Downloader
cd Scribd-Downloader
sudo pip install -r requirements.txt
sudo python scribd.py
```

Usage: `sudo python scribd.py <link of scribd document>`

◘ To download text from PDF's containing selectable text:
- example: `sudo python scribd.py https://www.scribd.com/document/55949937/33-Strategies-of-War`

◘ To download PDF's containing images; use the -p option:
- example: `sudo python scribd.py http://scribd.com/doc/17142797/Case-in-Point -p`

## Disclaimer:

Download softcopies of books maybe prohibited. Please support the Authors by buying their titles.

## License:

`The MIT License`
