#!/usr/bin/env python

import os
import sys
import shutil
from bs4 import BeautifulSoup


def parse_index(index_path):
    """Parses index.html file for chapters and sections."""

    index_file = open(index_path)
    soup = BeautifulSoup(index_file.read())
    scrape = {}
    chapters = [chap for chap in soup.ul.contents if chap != '\n']
    # chapters now contains a list of chapters (bs4 li elements)

    for chapter in chapters: # loop through chapters
        chapter_string = chapter.a.string
        if ':' in chapter_string:
            chapter_string = chapter_string[8:] # get ride of 'Chapter'
            chapter_string = chapter_string.replace(' ', '', 1) # delete space after colon
        chapter_file = chapter.a['href']
        chapter_tuple = (chapter_string, chapter_file)
        scrape[chapter_tuple] = []
        if chapter.li != None: # filter out non-content chapters
                               # (Preface, Acknowledgements, etc)
            for section in chapter.find_all('li'):
                section_string = section.a.string
                section_file = section.a['href']
                section_tuple = (section_string, section_file)
                scrape[chapter_tuple].append(section_tuple)

    return scrape


def create_structure(index_scrape):
    """
        Creates directory structure based off of data passed from the scraped
        index.html file.
    """

    os.mkdir(NEW_DIR)
    os.chdir(NEW_DIR)
    generate_course_index()
    generate_chapters(index_scrape)

    os.chdir('..')


def generate_course_index():
    """Generates the index.md for the entire course."""

    with open('index.md', 'w') as index:
        index.write('/*\n')
        index.write('Title: ' + NEW_DIR.replace('_', ' ') + '\n')
        index.write('layout: course\n')
        index.write('*/\n')


def generate_chapters(index_scrape):
    """Generates directories and content for each course chapter."""

    for tuple in index_scrape:
        (chapter_name, chapter_file) = tuple
        if ':' in chapter_name: # if it's actual content
            chapter_name = chapter_name.replace(' ', '_')
            try: # get number of chapter from title
                chapter_num = int(chapter_name[:2])
                offset = 3
            except ValueError:
                chapter_num = chapter_name[:1]
                offset = 2
            chapter_dir = '%s.%s' % (chapter_num, chapter_name[offset:])
            os.mkdir(chapter_dir)
            generate_chapter_content(chapter_dir, index_scrape[tuple])
        else: # non-content
            try:
                os.mkdir('Non-Content')
            except OSError:
                pass


def generate_chapter_content(chapter_dir, sections):
    """Populate with chapter directories with content."""

    for i, section in enumerate(sections, 1):
        section_file = '%d.%s.md' % (i, section[0].replace(' ', '_'))
        with open(chapter_dir + '/' + section_file, 'w') as lesson:
            lesson.write('')

def main():
    if len(sys.argv) != 2:
        print 'Usage: ./scraper.py [directory]'
        sys.exit()

    global DIR, NEW_DIR
    DIR = sys.argv[1]
    NEW_DIR = DIR.replace('-', '_')

    index_scrape = parse_index(DIR + '/index.html')
    create_structure(index_scrape)


if __name__ == '__main__':
    main()
