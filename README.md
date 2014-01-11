LAN LMS Content importing scripts 
=======
This repository contains a variety of importers/converters of Open Educational Resources to LAN Academy's Learning Management System. 

Supported OER
--------
###[2012 Books](http://2012books.lardbucket.org)
Link: http://2012books.lardbucket.org

License: Creative Commons by-nc-sa 3.0

Number of resources: 119

Description: An archive by Andy Schmitz of CC-licensed copies of all the books which were available online from an unnamed-at-request former-OER publisher at the end of 2012. 


Requirements/ Usage
------------
Todo


Known Bugs
-----------
Todo

Options for pages
-----------------

###Note on titles: 
Title: `Title of Course of Chapter` (Should equal folder if [ ]=[_] eg `/Title_of_Course_or_Chapter/`)
or
Title: `Title of Page` (Should equal url if [ ]=[_] eg `Title_of_Page.md`)

###Page types:

layout: Course
Title: `Title of Course` 
`@` Description of course, etc.

layout: Chapter
Title: `Title of Chapter` 
`@` A description of chapter and list of sub-pages

layout: Article
Title: `Title of Page` 
`@` The text

layout: Questions
Title: `Title of Page` 
`@` Open-ended questions with exam-boxs under them.

layout: Exam
Title: `Title of Page` 
open-notes: `[yes][no]` 
`@` The questions in our exam format (see demo)

keywords.xml
vocabulary-definitions list in form of <title>word</title><text>definition</text>