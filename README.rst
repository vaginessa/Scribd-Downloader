Scribd-Downloader
=================

|PyPi Version| |Build Status|

(A better online service I found https://dlscrib.com/, created by `Erik Fong`_).

-  This python script allows downloading of Scribd documents.

-  It does not matter if the pages are blurred or require
   authentication, this script will still do the job.

-  There are two types of documents on Scribd:

-  Documents made up using a collection of images and
-  Actual documents where the text can be selected, copied etc.

This script takes a different approach to both of them:

-  Documents consisting of a collection of images is straightforward and
   this script will simply download the induvidual images which can
   later be combined into a PDF using a suitable software. Simple.

-  Actual documents where the text can be selected are hard to tackle.
   If you feed such a document in this script, only the text present in
   document will be downloaded. I do not know much about JS and since
   Scribd uses JS to combine text and images for each induvidual page, I
   do not yet know how they do it. Ideas welcome on combining images and
   text!

Installation
------------

::

    pip install scribd-downloader

or if you like to live on the bleeding edge:

::

    pip install -r requirements.txt
    python setup.py install

Usage
-----

::

    usage: scribdl [-h] [-i] DOC

    Download documents/text from scribd.com

    positional arguments:
      DOC           scribd document to download

    optional arguments:
      -h, --help    show this help message and exit
      -i, --images  download document made up of images

-  To download text from document containing selectable text:
-  example:
   ``scribdl https://www.scribd.com/document/55949937/33-Strategies-of-War``

(Text will be saved side by side in a ``.txt`` file in your current
working directory)

-  To download document containing images; use the ``--images`` option (the tool cannot figure out this on its own):
-  example:
   ``scribdl -i http://scribd.com/doc/17142797/Case-in-Point``

(Images will be saved in your current working directory)

- It can also download books as PDFs but only the preview version will be downloaded (Scribd does not
  expose the full contents of the book unlike documents).
- To download the preview version of the book:
- example:
  ``scribdl https://www.scribd.com/read/189087235/Confessions-of-a-Casting-Director-Help-Actors-Land-Any-Role-with-Secrets-from-Inside-the-Audition-Room``

Contributing
------------

- Feel free to report bugs, documents failing to download, features or anything else.

- Even better, send a PR!

Disclaimer
----------

Downloading books from Scribd for free maybe prohibited. This tool is
meant for educational purposes only. Please support the authors by buying
their titles.

License
-------

``The MIT License``

.. |PyPi Version| image:: https://img.shields.io/pypi/v/scribd-downloader.svg
   :target: https://pypi.org/project/scribd-downloader

.. |Build Status| image:: https://travis-ci.org/ritiek/scribd-downloader.svg?branch=master
   :target: https://travis-ci.org/ritiek/scribd-downloader
   
.. _Erik Fong: mailto:dlscrib@gmail.com
