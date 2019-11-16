    :Author: Vikash
    :Date: November 8, 2019

.. contents::



1 Description
-------------

A simple scraper to scrape bugs and comments from bugzilla using the REST API

2 Prerequisites
---------------

Running the scraper only has three prerequisites:

- click

- tqdm

- requests

3 Installation
--------------

Clone this repository, create a new environment and use the command

.. code:: org

    pip install -e .

4 Usage
-------

Use the following command to scrape bugs

.. code:: org

    buscraper bugscrape <subdomain> -s <save_dir> -i <start_id> -f <end_id>

The above command scrapes all bugs from subdomain starting from id start\ :sub:`id`\ till
id end\ :sub:`id`\ and stores them in “save\ :sub:`dir`\/<subdomain>bugs/” directory. The bugs are stored in files year.jsonl

Once all the bugs have been scraped, you can scrape all the comments
corresponding to the scraped bugs by using the command:

.. code:: org

    buscraper commentscrape <subdomain> -s <save_dir>

The above command scrapes all comments and stores them in “save\ :sub:`dir`\/<subdomain>bugs/”
directory. The bugs are stored in files year\ :sub:`comments.jsonl`\. A metadata file is
also created (“bug\ :sub:`metadata.jsonl`\”) that has information about all bug\ :sub:`ids`\
scraped, their year and the associated comment\ :sub:`ids`\.

5 Troubleshooting
-----------------

It is possible that the request sent is too large and might lead to issues.
Try reducing the chunk size using option -c while scraping bugs.
