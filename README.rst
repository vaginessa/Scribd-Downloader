Scribd-Downloader
=================

|PyPi Version| |Build Status|

(I also found an online service https://dlscrib.com/ created by `Erik Fong`_. It doesn't
use this script as some people seem to think!).

This python script allows downloading of Scribd documents. It does not matter if the pages
are blurred or require authentication, this script will still do its job.

There are two types of documents on Scribd:

-  Documents made up using a collection of images and
-  Actual documents where the text can be selected, copied etc.

This script takes a different approach to both of them:

-  Documents consisting of a collection of images is straightforward and
   this script will simply download the induvidual images which can
   be combined to ``.pdf`` by passing ``--pdf`` option to the tool. Simple.

-  Actual documents where the text can be selected are hard to tackle.
   If we feed such a document to this tool, only the text present in
   document will be downloaded. Scribd seems to use javascript to somehow
   combine text and images. So far, I haven't been able to combine them
   with Python in a way they look like the original document.

Installation
------------

Make sure you're using Python 3 (Python 2 is not supported by a few dependencies).
Then run these commands:

::

    $ pip install scribd-downloader

or install the development version with:

::

    $ python setup.py install

Usage
-----

::

    usage: scribdl [-h] [-i] [-p] URL

    Download documents and books from scribd.com

    positional arguments:
      URL           scribd url to download

    optional arguments:
      -h, --help    show this help message and exit
      -i, --images  download url made up of images
      -p, --pdf     convert to pdf (*Nix: imagemagick)

Examples
--------

Downloading text from document containing selectable text:
::
   $ scribdl https://www.scribd.com/document/55949937/33-Strategies-of-War

(Text will be saved side by side in a ``.md`` file in the current
working directory)

Download document containing images; use the ``--images`` option (the tool cannot figure out this on its own):
::
    $ scribdl -i http://scribd.com/doc/17142797/Case-in-Point

(Images will be saved in the current working directory)

~~It can also download books but only the preview version will be downloaded (Scribd does not
expose the full contents of the book unlike documents).~~

It can now also download complete books by mimicking itself as a premium user!
This will generate an ``.md`` file in the current working directory:

::
    $ scribdl https://www.scribd.com/read/189087235/Confessions-of-a-Casting-Director-Help-Actors-Land-Any-Role-with-Secrets-from-Inside-the-Audition-Room

Pass ``--pdf`` option to convert the generated output to a PDF.

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
