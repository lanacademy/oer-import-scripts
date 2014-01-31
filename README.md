LAN LMS Content importing scripts
=======
This repository contains a variety of importers/converters of Open Educational
Resources to LAN Academy's Learning Management System.

Supported OER
--------
###[2012 Books](http://2012books.lardbucket.org)
Link: http://2012books.lardbucket.org

License: Creative Commons by-nc-sa 3.0

Number of resources: 119

Description: An archive by Andy Schmitz of CC-licensed copies of all the books
which were available online from an unnamed-at-request former-OER publisher at
the end of 2012.

Requirements/ Usage
------------

- `2012books_scraper.py` requires the BeautifulSoup4 HTML parsing library
  for Python
    - If you have `pip` on your system you can install it by simply
      running `pip install -r requirements.txt`

To use `2012books_scraper.py`, go to [2012 Books](http://2012books.lardbucket.org)
and download a course as a zip file. Unzip it into the same directory as the
script. Ensure that you have BeautifulSoup (see above), and then simply run

    $ ./2012books_scraper.py [unzipped directory]

and it will produced another directory containing the book with directories
for each chapter, etc.

Known Bugs
-----------

See the [issues](http://github.com/lanacademy/oer-import-scripts/issues).

Options for pages
-----------------

###Note on titles:
Title of a page should equal the url of that page with underscores=spaces.

Examples:

	Title: Title of Course of Chapter = /Title_of_Course_or_Chapter/
	Title: Title of Page = Title_of_Page.md

###Page types:

	layout: Course
	Title: Title of Course
	@ Description of course, etc.

	layout: Chapter
	Title: Title of Chapter
	@ A description of chapter and list of sub-pages

	layout: Article
	Title: Title of Page
	@ The text

	layout: Questions
	Title: Title of Page
	@ Open-ended questions with exam-boxs under them.

	layout: Exam
	Title: Title of Page
	open-notes: [yes][no]
	@ The questions in our exam format (see demo)

	keywords.xml
	vocabulary-definitions list in form of <title>word</title><text>definition</text>
