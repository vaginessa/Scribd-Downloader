#!/usr/bin/env python

from setuptools import setup, find_packages
import scribdl

with open("README.rst", "r") as f:
    long_description = f.read()

setup(name='scribd-downloader',
      version=scribdl.__version__,
      description='Download documents/text from scribd.com',
      long_description=long_description,
      author='Ritiek Malhotra',
      author_email='ritiekmalhotra123@gmail.com',
      packages = find_packages(),
      entry_points={
            'console_scripts': [
                  'scribdl = scribdl.command_line:_command_line',
            ]
      },
      url='https://www.github.com/ritiek/scribd-downloader',
      keywords=['scribd-downloader', 'documents', 'command-line', 'python'],
      license='MIT',
      download_url='https://github.com/ritiek/scribd-downloader/archive/v' + scribdl.__version__ + '.tar.gz',
      classifiers=[],
      install_requires=[
            'requests',
            'BeautifulSoup4',
            'img2pdf',
            'md2pdf'
      ]
     )
